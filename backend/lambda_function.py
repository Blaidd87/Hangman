"""
Hangman Multiplayer - AWS Lambda WebSocket Handlers
Deploy this as a single Lambda function with API Gateway WebSocket API.
"""

import json
import os
import random
import string
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key


def convert_decimals(obj):
    """Convert DynamoDB Decimal types to Python int/float for JSON serialization."""
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE', 'HangmanConnections'))
games_table = dynamodb.Table(os.environ.get('GAMES_TABLE', 'HangmanGames'))

# Word list (subset for Lambda - full list would be loaded from S3 in production)
WORDS = [
    "python", "hangman", "programming", "computer", "keyboard", "developer",
    "algorithm", "function", "variable", "software", "terminal", "debugging",
    "interface", "database", "network", "javascript", "frontend", "backend",
    "multiplayer", "websocket", "lambda", "server", "client", "browser"
]


def generate_room_code():
    """Generate a 4-character room code."""
    return ''.join(random.choices(string.ascii_uppercase, k=4))


def get_api_gateway_client(event):
    """Create API Gateway Management API client."""
    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    endpoint = f"https://{domain}/{stage}"
    return boto3.client('apigatewaymanagementapi', endpoint_url=endpoint)


def send_to_connection(api_client, connection_id, data):
    """Send message to a specific connection."""
    try:
        api_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8')
        )
        return True
    except api_client.exceptions.GoneException:
        # Connection no longer exists, clean up
        try:
            connections_table.delete_item(Key={'connectionId': connection_id})
        except Exception:
            pass
        return False


def broadcast_to_room(api_client, room_id, data, exclude_connection=None):
    """Send message to all connections in a room."""
    response = connections_table.query(
        IndexName='RoomIndex',
        KeyConditionExpression=Key('roomId').eq(room_id)
    )
    for item in response.get('Items', []):
        conn_id = item['connectionId']
        if conn_id != exclude_connection:
            send_to_connection(api_client, conn_id, data)


def get_game_state(game):
    """Get sanitized game state for clients."""
    state = {
        'roomId': game['roomId'],
        'wordLength': len(game['word']),
        'guessedLetters': list(game.get('guessedLetters', set())),
        'wrongGuesses': game.get('wrongGuesses', 0),
        'maskedWord': ''.join(
            letter if letter in game.get('guessedLetters', set()) else '_'
            for letter in game['word']
        ),
        'status': game.get('status', 'waiting'),
        'players': game.get('players', []),
        'currentTurn': game.get('currentTurn', 0),
        'maxWrongGuesses': 6
    }
    return convert_decimals(state)


def handle_connect(event):
    """Handle WebSocket $connect."""
    connection_id = event['requestContext']['connectionId']
    connections_table.put_item(Item={
        'connectionId': connection_id,
        'roomId': 'lobby'
    })
    return {'statusCode': 200}


def handle_disconnect(event):
    """Handle WebSocket $disconnect."""
    connection_id = event['requestContext']['connectionId']

    # Get connection info
    try:
        response = connections_table.get_item(Key={'connectionId': connection_id})
        item = response.get('Item', {})
        room_id = item.get('roomId')
        player_name = item.get('playerName')

        # Remove from room if in one
        if room_id and room_id != 'lobby':
            try:
                game = games_table.get_item(Key={'roomId': room_id}).get('Item')
                if game:
                    players = game.get('players', [])
                    players = [p for p in players if p.get('connectionId') != connection_id]

                    if players:
                        games_table.update_item(
                            Key={'roomId': room_id},
                            UpdateExpression='SET players = :p',
                            ExpressionAttributeValues={':p': players}
                        )
                        # Notify remaining players
                        api_client = get_api_gateway_client(event)
                        broadcast_to_room(api_client, room_id, {
                            'action': 'playerLeft',
                            'playerName': player_name,
                            'players': [p.get('name') for p in players]
                        })
                    else:
                        # No players left, delete game
                        games_table.delete_item(Key={'roomId': room_id})
            except Exception:
                pass
    except Exception:
        pass

    # Delete connection
    try:
        connections_table.delete_item(Key={'connectionId': connection_id})
    except Exception:
        pass

    return {'statusCode': 200}


def handle_create_room(event, body):
    """Create a new game room."""
    connection_id = event['requestContext']['connectionId']
    player_name = body.get('playerName', 'Player 1')

    # Generate unique room code
    room_id = generate_room_code()
    while True:
        existing = games_table.get_item(Key={'roomId': room_id}).get('Item')
        if not existing:
            break
        room_id = generate_room_code()

    # Create game
    word = random.choice(WORDS).lower()
    game = {
        'roomId': room_id,
        'word': word,
        'guessedLetters': set(),
        'wrongGuesses': 0,
        'status': 'waiting',
        'players': [{'connectionId': connection_id, 'name': player_name}],
        'currentTurn': 0,
        'hostConnectionId': connection_id
    }

    # DynamoDB doesn't support empty sets, convert to list
    game_for_db = {**game, 'guessedLetters': []}
    games_table.put_item(Item=game_for_db)

    # Update connection
    connections_table.update_item(
        Key={'connectionId': connection_id},
        UpdateExpression='SET roomId = :r, playerName = :n',
        ExpressionAttributeValues={':r': room_id, ':n': player_name}
    )

    api_client = get_api_gateway_client(event)
    send_to_connection(api_client, connection_id, {
        'action': 'roomCreated',
        'roomId': room_id,
        'gameState': get_game_state(game)
    })

    return {'statusCode': 200}


def handle_join_room(event, body):
    """Join an existing game room."""
    connection_id = event['requestContext']['connectionId']
    room_id = body.get('roomId', '').upper()
    player_name = body.get('playerName', 'Player 2')

    api_client = get_api_gateway_client(event)

    # Get game
    response = games_table.get_item(Key={'roomId': room_id})
    game = response.get('Item')

    if not game:
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Room not found'
        })
        return {'statusCode': 200}

    # Allow joining if fewer than 2 players (regardless of game status)
    players = game.get('players', [])
    if len(players) >= 2:
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Room is full'
        })
        return {'statusCode': 200}

    # Add player
    players.append({'connectionId': connection_id, 'name': player_name})

    # Reset game if it was finished, or start if waiting
    word = game.get('word')
    if game.get('status') in ('won', 'lost'):
        # Start fresh game
        word = random.choice(WORDS).lower()
        game['guessedLetters'] = set()
        game['wrongGuesses'] = 0
        game['currentTurn'] = 0
    else:
        game['guessedLetters'] = set(game.get('guessedLetters', []))

    game['word'] = word
    game['players'] = players
    game['status'] = 'playing'

    games_table.update_item(
        Key={'roomId': room_id},
        UpdateExpression='SET players = :p, #s = :st, word = :w, guessedLetters = :g, wrongGuesses = :wg, currentTurn = :t',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':p': players,
            ':st': 'playing',
            ':w': game['word'],
            ':g': list(game['guessedLetters']),
            ':wg': game.get('wrongGuesses', 0),
            ':t': game.get('currentTurn', 0)
        }
    )

    # Update connection
    connections_table.update_item(
        Key={'connectionId': connection_id},
        UpdateExpression='SET roomId = :r, playerName = :n',
        ExpressionAttributeValues={':r': room_id, ':n': player_name}
    )

    # Notify all players
    game_state = get_game_state(game)
    broadcast_to_room(api_client, room_id, {
        'action': 'gameStarted',
        'gameState': game_state
    })

    return {'statusCode': 200}


def handle_guess(event, body):
    """Handle a letter guess."""
    connection_id = event['requestContext']['connectionId']
    letter = body.get('letter', '').lower()

    api_client = get_api_gateway_client(event)

    if not letter or len(letter) != 1 or not letter.isalpha():
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Invalid guess'
        })
        return {'statusCode': 200}

    # Get connection info
    conn_response = connections_table.get_item(Key={'connectionId': connection_id})
    conn_item = conn_response.get('Item', {})
    room_id = conn_item.get('roomId')
    player_name = conn_item.get('playerName', 'Unknown')

    if not room_id or room_id == 'lobby':
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Not in a game'
        })
        return {'statusCode': 200}

    # Get game
    response = games_table.get_item(Key={'roomId': room_id})
    game = response.get('Item')

    if not game or game.get('status') != 'playing':
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Game not active'
        })
        return {'statusCode': 200}

    # Check if it's this player's turn
    players = game.get('players', [])
    current_turn = int(game.get('currentTurn', 0))

    if current_turn < len(players):
        current_player = players[current_turn]
        if current_player.get('connectionId') != connection_id:
            send_to_connection(api_client, connection_id, {
                'action': 'error',
                'message': 'Not your turn'
            })
            return {'statusCode': 200}

    # Process guess
    guessed_letters = set(game.get('guessedLetters', []))

    if letter in guessed_letters:
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Letter already guessed'
        })
        return {'statusCode': 200}

    guessed_letters.add(letter)
    word = game['word']
    wrong_guesses = int(game.get('wrongGuesses', 0))

    correct = letter in word
    if not correct:
        wrong_guesses += 1

    # Update turn
    next_turn = (current_turn + 1) % len(players)

    # Check win/lose
    won = all(l in guessed_letters for l in word)
    lost = wrong_guesses >= 6

    status = 'playing'
    if won:
        status = 'won'
    elif lost:
        status = 'lost'

    # Update game
    game['guessedLetters'] = guessed_letters
    game['wrongGuesses'] = wrong_guesses
    game['status'] = status
    game['currentTurn'] = next_turn

    games_table.update_item(
        Key={'roomId': room_id},
        UpdateExpression='SET guessedLetters = :g, wrongGuesses = :w, #s = :st, currentTurn = :t',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':g': list(guessed_letters),
            ':w': wrong_guesses,
            ':st': status,
            ':t': next_turn
        }
    )

    # Broadcast update
    game_state = get_game_state(game)
    if status in ('won', 'lost'):
        game_state['word'] = word  # Reveal word on game end

    broadcast_to_room(api_client, room_id, {
        'action': 'guessResult',
        'letter': letter,
        'correct': correct,
        'playerName': player_name,
        'gameState': game_state
    })

    return {'statusCode': 200}


def handle_new_game(event, body):
    """Start a new game in the same room."""
    connection_id = event['requestContext']['connectionId']

    api_client = get_api_gateway_client(event)

    # Get connection info
    conn_response = connections_table.get_item(Key={'connectionId': connection_id})
    conn_item = conn_response.get('Item', {})
    room_id = conn_item.get('roomId')

    if not room_id or room_id == 'lobby':
        return {'statusCode': 200}

    # Get game
    response = games_table.get_item(Key={'roomId': room_id})
    game = response.get('Item')

    if not game:
        return {'statusCode': 200}

    # Only host can start new game
    if game.get('hostConnectionId') != connection_id:
        send_to_connection(api_client, connection_id, {
            'action': 'error',
            'message': 'Only host can start new game'
        })
        return {'statusCode': 200}

    # Reset game
    word = random.choice(WORDS).lower()
    games_table.update_item(
        Key={'roomId': room_id},
        UpdateExpression='SET word = :w, guessedLetters = :g, wrongGuesses = :wg, #s = :st, currentTurn = :t',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':w': word,
            ':g': [],
            ':wg': 0,
            ':st': 'playing',
            ':t': 0
        }
    )

    game['word'] = word
    game['guessedLetters'] = set()
    game['wrongGuesses'] = 0
    game['status'] = 'playing'
    game['currentTurn'] = 0

    broadcast_to_room(api_client, room_id, {
        'action': 'newGame',
        'gameState': get_game_state(game)
    })

    return {'statusCode': 200}


def lambda_handler(event, context):
    """Main Lambda handler for WebSocket API."""
    route_key = event['requestContext'].get('routeKey', '')

    if route_key == '$connect':
        return handle_connect(event)

    if route_key == '$disconnect':
        return handle_disconnect(event)

    # Parse body for other routes
    body = {}
    if event.get('body'):
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {'statusCode': 400, 'body': 'Invalid JSON'}

    action = body.get('action', route_key)

    handlers = {
        'createRoom': handle_create_room,
        'joinRoom': handle_join_room,
        'guess': handle_guess,
        'newGame': handle_new_game,
    }

    handler = handlers.get(action)
    if handler:
        return handler(event, body)

    return {'statusCode': 400, 'body': f'Unknown action: {action}'}
