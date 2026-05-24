````md
# Mystery Word Backend

Backend API and realtime websocket server for the Mystery Word multiplayer guessing game.

Built with:

- FastAPI
- Redis
- MongoDB
- LangChain
- Groq LLM
- WebSockets

---

# Features

- Realtime multiplayer gameplay
- WebSocket-based communication
- AI-powered question answering
- Session management using Redis
- Leaderboard system
- Recent games history
- Spectator live chat
- Automatic session expiration
- Difficulty-based point system

---

# Tech Stack

- Python
- FastAPI
- Redis
- MongoDB
- Motor
- LangChain
- Groq API

---

# Project Structure

```bash
backend/
│
├── main.py
├── agent.py
├── data.py
├── requirements.txt
├── .env
└── README.md
```
````

---

# Environment Variables

Create a `.env` file:

```env
API_KEY=your_groq_api_key
MODEL_NAME=llama-3.1-8b-instant
```

---

# Installation

## 1. Clone Repository

```bash
git clone <backend-repo-url>
cd backend
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running Services

## Start MongoDB

Make sure MongoDB is running locally:

```bash
mongodb://localhost:27017
```

---

## Start Redis / Memurai

Default Redis port:

```bash
localhost:6379
```

---

# Start Backend Server

```bash
uvicorn main:app --reload
```

Server runs on:

```bash
http://127.0.0.1:8000
```

---

# Frontend Repository

[Frontend Repository](https://github.com/07ReuelBodhak/MysteryWord)

---

# API Endpoints

## Create Game

```http
POST /game/create
```

---

## Get Active Games

```http
GET /game/active
```

---

## Get Game Session

```http
GET /game/{session_id}
```

Query:

```http
?discord_id=123
```

---

# WebSocket Endpoint

```ws
/ws/{session_id}
```

---

# WebSocket Events

## Ask Question

```json
{
  "type": "ask_question",
  "question": "Is it an animal?"
}
```

---

## Final Guess

```json
{
  "type": "final_guess",
  "guess": "Tiger"
}
```

---

## Spectator Chat

```json
{
  "type": "chat_message",
  "username": "icey",
  "message": "hello"
}
```

---

# AI System

The backend uses:

- LangChain agents
- Groq LLM
- Structured JSON responses

The AI only responds with:

```json
{
  "response": "Yes"
}
```

Possible values:

- Yes
- No
- Maybe

---

# Leaderboard System

Difficulty-based scoring:

| Difficulty | Win | Loss |
| ---------- | --- | ---- |
| Easy       | +10 | -20  |
| Medium     | +15 | -10  |
| Hard       | +30 | -5   |

---

# Recent Games System

Stores latest 5 games per user.

Each entry includes:

- Difficulty
- Result
- Hidden word
- Played timestamp

---

# Session Flow

1. Player creates game
2. Session stored in Redis
3. WebSocket room created
4. AI answers questions
5. Game ends on:
   - Correct guess
   - Timeout

6. Leaderboard updates
7. Recent game added
8. Session cleaned automatically

---

# Future Improvements

- Ranked matchmaking
- Spectator joining system
- AI memory improvements
- Better prompt engineering
- Analytics dashboard
- Global leaderboard
- Game categories

---

# Author

Built by Reuel
