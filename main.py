from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)

from fastapi.middleware.cors import CORSMiddleware

from motor.motor_asyncio import AsyncIOMotorClient

from redis.asyncio import Redis

from data import get_word

from pydantic import BaseModel

import uuid
import time
import json
import random
import asyncio

# =========================================================
# DATABASE
# =========================================================

mongo_client = AsyncIOMotorClient(
    "mongodb://localhost:27017"
)

db = mongo_client["mystery-word"]
leaderboard_col = db["leaderboards"]

# =========================================================
# REDIS
# =========================================================

redis_client = Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

# =========================================================
# APP
# =========================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# WEBSOCKET MANAGER
# =========================================================

class ConnectionManager:

    def __init__(self):

        # session_id -> [websockets]
        self.active_connections = {}

    async def connect(
        self,
        session_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(
            websocket
        )

        print(f"CONNECTED -> {session_id}")

    def disconnect(
        self,
        session_id: str,
        websocket: WebSocket,
    ):

        if session_id in self.active_connections:

            if websocket in self.active_connections[session_id]:

                self.active_connections[
                    session_id
                ].remove(websocket)

            if len(
                self.active_connections[session_id]
            ) == 0:

                del self.active_connections[session_id]

        print(f"DISCONNECTED -> {session_id}")

    async def broadcast(
        self,
        session_id: str,
        message: dict,
    ):

        if session_id not in self.active_connections:
            return

        dead_connections = []

        for connection in self.active_connections[
            session_id
        ]:

            try:

                await connection.send_text(
                    json.dumps(message)
                )

            except:

                dead_connections.append(
                    connection
                )

        for dead in dead_connections:

            self.disconnect(
                session_id,
                dead,
            )


manager = ConnectionManager()

# =========================================================
# REQUEST MODELS
# =========================================================

class CreateGameRequest(BaseModel):
    discord_id: str
    username: str


class AskQuestionRequest(BaseModel):
    question: str


class FinalGuessRequest(BaseModel):
    guess: str


class SpectatorMessageRequest(BaseModel):
    username: str
    message: str

# =========================================================
# HELPERS
# =========================================================

SESSION_DURATION = 300


async def get_session(session_id: str):

    raw_session = await redis_client.get(
        f"session:{session_id}"
    )

    if not raw_session:

        raise HTTPException(
            status_code=404,
            detail="Game session expired or not found",
        )

    return json.loads(raw_session)


def get_remaining_seconds(session):

    remaining = int(
        session["expires_at"] - time.time()
    )

    return max(0, remaining)


async def save_session(
    session_id: str,
    session_data: dict,
):

    await redis_client.set(
        f"session:{session_id}",
        json.dumps(session_data),
    )

# =========================================================
# LEADERBOARD UPDATE
# =========================================================

async def update_leaderboard(
    discord_id: str,
    username: str,
    difficulty: str,
    result: str,  # "win" or "loss"
):

    points_map = {
        "easy": {"win": 10, "loss": -20},
        "medium": {"win": 15, "loss": -10},
        "hard": {"win": 30, "loss": -5},
    }

    points = points_map[difficulty][result]

    await leaderboard_col.update_one(
        {"discord_id": discord_id},

        {
            # update static info (safe overwrite)
            "$set": {
                "username": username,
            },

            # ONLY increments (no conflict possible)
            "$inc": {
                "total_points": points,
                "wins": 1 if result == "win" else 0,
                "losses": 1 if result == "loss" else 0,
                "games_played": 1,
            },
        }
    )

# =========================================================
# SESSION TIMER
# =========================================================
async def session_timer(session_id: str):

    try:
        while True:

            raw_session = await redis_client.get(f"session:{session_id}")

            if not raw_session:
                return

            session = json.loads(raw_session)
            print("session : ",session)

            # If session already ended somewhere else, stop timer
            if session["status"] != "active":
                return

            remaining = session["expires_at"] - time.time()

            if remaining <= 0:
                break

            await asyncio.sleep(1)

        # ===================== TIMEOUT OCCURRED =====================

        # IMPORTANT: re-fetch to avoid race condition
        raw_session = await redis_client.get(f"session:{session_id}")

        if not raw_session:
            return

        session = json.loads(raw_session)

        if session["status"] != "active":
            return

        session["status"] = "expired"
        await save_session(session_id, session)

        # ===================== LEADERBOARD LOSS UPDATE =====================
        await update_leaderboard(
            session["player_id"],
            session["player_username"],
            session["difficulty"],
            "loss",
        )

        # ===================== BROADCAST GAME OVER =====================
        await manager.broadcast(
            session_id,
            {
                "type": "game_over",
                "result": "timeout",
                "word": session["word"],
            },
        )

        # give frontend time to show UI
        await asyncio.sleep(5)

        # ===================== CLEANUP =====================
        await redis_client.delete(f"session:{session_id}")

        print(f"SESSION EXPIRED -> {session_id}")

    except Exception as e:
        print("SESSION TIMER ERROR:", e)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():

    return {
        "message": "Mystery Word API Running"
    }

# =========================================================
# CREATE GAME
# =========================================================

@app.post("/game/create")
async def create_game(
    request: CreateGameRequest
):

    session_id = str(uuid.uuid4())

    random_word = get_word()

    # difficulty

    if len(random_word) <= 5:

        difficulty = "easy"

    elif len(random_word) <= 8:

        difficulty = "medium"

    else:

        difficulty = "hard"

    now = time.time()

    session_data = {

        "word": random_word,

        "player_id":
            request.discord_id,

        "player_username":
            request.username,

        "spectators": [],

        "chat_messages": [],

        "questions": [],

        "difficulty":
            difficulty,

        "started_at": now,

        "expires_at":
            now + SESSION_DURATION,

        "status": "active",
    }

    # IMPORTANT:
    # NO TTL HERE

    await redis_client.set(
        f"session:{session_id}",
        json.dumps(session_data),
    )

    asyncio.create_task(
        session_timer(session_id)
    )

    print(
        f"NEW GAME -> {session_id}"
    )

    return {

        "session_id":
            session_id,

        "difficulty":
            difficulty,
    }

# =========================================================
# ACTIVE GAMES
# =========================================================

@app.get("/game/active")
async def get_active_games():

    games = []

    keys = await redis_client.keys(
        "session:*"
    )

    for key in keys:

        raw_session = await redis_client.get(
            key
        )

        if not raw_session:
            continue

        session = json.loads(
            raw_session
        )

        if session["status"] != "active":
            continue

        session_id = key.split(":")[1]

        games.append({

            "session_id":
                session_id,

            "title":
                f"{session['player_username']}'s Game",

            "difficulty":
                session["difficulty"],

            "questions_count":
                len(
                    session["questions"]
                ),

            "spectator_count":
                len(
                    session["spectators"]
                ),

            "remaining_seconds":
                get_remaining_seconds(
                    session
                ),

            "status":
                session["status"],
        })

    return games

# =========================================================
# GET GAME SESSION
# =========================================================

@app.get("/game/{session_id}")
async def get_game_session(
    session_id: str,
    discord_id: str = Query(...),
):

    session = await get_session(
        session_id
    )

    is_player = (
        session["player_id"]
        == discord_id
    )

    return {

        "id": session_id,

        "isPlayer":
            is_player,

        "difficulty":
            session["difficulty"],

        "questions":
            session["questions"],

        "chat_messages":
            session["chat_messages"],

        "spectatorCount":
            len(
                session["spectators"]
            ),

        "durationSeconds":
            SESSION_DURATION,

        "remainingSeconds":
            get_remaining_seconds(
                session
            ),

        "startedAt":
            session["started_at"],

        "status":
            session["status"],
    }

# =========================================================
# WEBSOCKET
# =========================================================


@app.websocket("/ws/{session_id}")
async def ws(websocket: WebSocket, session_id: str):

    await manager.connect(session_id, websocket)

    try:
        while True:
            data = json.loads(await websocket.receive_text())

            session = await get_session(session_id)

            # ===================== ASK QUESTION =====================
            if data["type"] == "ask_question":

                answer = random.choice(["Yes", "No", "Maybe"])

                q = {
                    "question": data["question"],
                    "answer": answer,
                }

                session["questions"].append(q)
                await save_session(session_id, session)

                await manager.broadcast(session_id, {
                    "type": "question_answered",
                    "data": q,
                })

            # ===================== FINAL GUESS =====================
            elif data["type"] == "final_guess":

                guess = data["guess"]
                correct = session["word"]

                is_correct = guess.strip().lower() == correct.strip().lower()

                if is_correct:

                    session["status"] = "finished"
                    await save_session(session_id, session)

                    # ✅ WIN LEADERBOARD UPDATE
                    await update_leaderboard(
                        session["player_id"],
                        session["player_username"],
                        session["difficulty"],
                        "win",
                    )

                    await manager.broadcast(session_id, {
                        "type": "game_over",
                        "result": "win",
                        "word": correct,
                    })

                    await asyncio.sleep(5)
                    await redis_client.delete(f"session:{session_id}")

                else:

                    await manager.broadcast(session_id, {
                        "type": "wrong_guess",
                        "guess": guess,
                    })

            # ===================== CHAT =====================
            elif data["type"] == "chat_message":

                msg = {
                    "sender": data["username"],
                    "message": data["message"],
                }

                session["chat_messages"].append(msg)
                await save_session(session_id, session)

                await manager.broadcast(session_id, {
                    "type": "spectator_message",
                    "data": msg,
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

    except Exception as e:
        print("WS ERROR:", e)
        manager.disconnect(session_id, websocket)