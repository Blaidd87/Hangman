# AWS Deployment Instructions

Follow these steps to deploy the Hangman multiplayer backend via AWS Console.

## Step 1: Create DynamoDB Tables

### Table 1: HangmanConnections

1. Go to **DynamoDB** in AWS Console
2. Click **Create table**
3. Settings:
   - Table name: `HangmanConnections`
   - Partition key: `connectionId` (String)
4. Click **Create table**
5. After creation, go to **Indexes** tab
6. Click **Create index**:
   - Partition key: `roomId` (String)
   - Index name: `RoomIndex`
   - Click **Create index**

### Table 2: HangmanGames

1. Click **Create table**
2. Settings:
   - Table name: `HangmanGames`
   - Partition key: `roomId` (String)
3. Click **Create table**

---

## Step 2: Create Lambda Function

1. Go to **Lambda** in AWS Console
2. Click **Create function**
3. Settings:
   - Function name: `HangmanWebSocket`
   - Runtime: `Python 3.11`
   - Architecture: `x86_64`
4. Click **Create function**
5. In the code editor, replace the default code with contents of `lambda_function.py`
6. Click **Deploy**

### Configure Environment Variables

1. Go to **Configuration** tab → **Environment variables**
2. Click **Edit** → **Add environment variable**:
   - `CONNECTIONS_TABLE` = `HangmanConnections`
   - `GAMES_TABLE` = `HangmanGames`
3. Click **Save**

### Configure Permissions

1. Go to **Configuration** tab → **Permissions**
2. Click the role name (opens IAM)
3. Click **Add permissions** → **Attach policies**
4. Search and attach: `AmazonDynamoDBFullAccess`
5. Click **Add permissions**

### Add Execute API Permission

1. Go to **Configuration** tab → **Permissions**
2. Click **Add permissions** → **Create inline policy**
3. Choose JSON tab and paste:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "execute-api:ManageConnections",
            "Resource": "arn:aws:execute-api:*:*:*/@connections/*"
        }
    ]
}
```
4. Click **Next**, name it `APIGatewayManageConnections`, click **Create policy**

---

## Step 3: Create API Gateway WebSocket API

1. Go to **API Gateway** in AWS Console
2. Click **Create API**
3. Choose **WebSocket API** → **Build**
4. Settings:
   - API name: `HangmanAPI`
   - Route selection expression: `$request.body.action`
5. Click **Next**

### Add Routes

Add these routes (click **Add route** for each):
- `$connect`
- `$disconnect`
- `$default`
- `createRoom`
- `joinRoom`
- `guess`
- `newGame`

Click **Next**

### Attach Integration

1. For each route, choose:
   - Integration type: **Lambda**
   - Lambda function: `HangmanWebSocket`
2. Click **Next**

### Add Stage

1. Stage name: `prod`
2. Click **Next** → **Create and deploy**

### Get WebSocket URL

1. Go to **Stages** → **prod**
2. Copy the **WebSocket URL** (looks like `wss://xxxxxx.execute-api.region.amazonaws.com/prod`)

---

## Step 4: Update Frontend

1. Open `multiplayer.html`
2. Find this line near the top:
```javascript
const WS_URL = 'wss://YOUR-API-ID.execute-api.YOUR-REGION.amazonaws.com/prod';
```
3. Replace with your WebSocket URL from Step 3

---

## Step 5: Test

1. Open `multiplayer.html` in browser
2. Enter a name and click **Create Room**
3. Copy the room code
4. Open in another browser/tab, enter name and room code, click **Join Room**
5. Play!

---

## Costs (Free Tier)

- **Lambda**: 1M free requests/month
- **DynamoDB**: 25GB storage, 25 read/write units free
- **API Gateway**: 1M WebSocket messages/month free

This setup should cost $0 for casual use.

---

## Troubleshooting

### "Internal server error" on connect
- Check Lambda has DynamoDB permissions
- Check environment variables are set

### Messages not received
- Check Lambda has `execute-api:ManageConnections` permission
- Check WebSocket URL is correct in frontend

### Room not found
- Room codes expire when all players disconnect
- Create a new room
