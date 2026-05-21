from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from data import get_word
import uuid
import time
from pydantic import BaseModel

client = AsyncIOMotorClient("mongodb://localhost:27017")

db = client['mystery-word']

app = FastAPI()

active_sessions = {}

class CreateGameRequest(BaseModel):
    discord_id: str
    username : str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/game/active")
async def get_active_games():

    games = []

    for session_id, session in active_sessions.items():

        games.append({

            "session_id": session_id,

            "title": f"{session['player_username']}'s Game",

            "difficulty": session["difficulty"],

            "questions_count": len(session["questions"]),

            "spectator_count": len(session["spectators"]),

            "status": session["status"],
        })

    return games

@app.post("/game/create")
async def create_game(request: CreateGameRequest):

    session_id = str(uuid.uuid4())

    discord_id = request.discord_id

    username = request.username

    random_word = get_word()

    if len(random_word) <= 5:
        difficulty = "easy"

    elif len(random_word) <= 8:
        difficulty = "medium"

    else:
        difficulty = "hard"

    active_sessions[session_id] = {

        "word": random_word,

        "player_id": discord_id,

        "player_username": username,

        "player": None,

        "spectators": [],

        "chat_messages": [],

        "questions": [],

        "difficulty": difficulty,

        "started_at": time.time(),

        "status": "active",
    }

    print("NEW GAME CREATED")

    print(active_sessions)

    return {
        "session_id": session_id,
        "difficulty": difficulty
    }