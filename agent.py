from dotenv import load_dotenv

import os

# from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_groq import ChatGroq

from typing import TypedDict, Literal

from langchain.agents import create_agent

from langchain.messages import SystemMessage, HumanMessage

load_dotenv()

model = ChatGroq(model=os.getenv("MODEL_NAME"), api_key=os.getenv('API_KEY'))

class GuessAnswer(TypedDict):
    response: Literal["Yes", "No", "Maybe"]

system_prompt = SystemMessage(
    content=(
        "You are a guessing-game assistant.\n\n"

        "You answer questions about a hidden word.\n\n"

        "IMPORTANT:\n"
        "Use COMMON HUMAN GUESSING-GAME LOGIC, not strict scientific logic.\n"
        "For example:\n"
        "- Birds are NOT considered animals.\n"
        "- Fish are NOT considered animals.\n"
        "- Insects are NOT considered animals.\n"
        "- Fruits and vegetables are treated separately.\n"
        "- Vehicles and machines are treated separately.\n\n"

        "You must answer based on what an average human would expect "
        "in a casual guessing game.\n\n"

        "STRICT RULES:\n"
        "- You MUST return valid JSON only.\n"
        "- Format must be: {\"response\": \"Yes\"}\n"
        "- response must ONLY be one of:\n"
        "  - Yes\n"
        "  - No\n"
        "  - Maybe\n"
        "- Do NOT include explanations.\n"
        "- Do NOT include extra text.\n"
        "- Do NOT reveal the hidden word.\n"
        "- Do NOT give hints.\n\n"

        "DECISION RULES:\n"
        "- Yes = clearly true in normal guessing-game logic.\n"
        "- No = clearly false in normal guessing-game logic.\n"
        "- Maybe = partially true, context-dependent, or ambiguous.\n\n"

        "EXAMPLES:\n\n"

        "Hidden word: Woodpecker\n"
        "User: Is it an animal?\n"
        "Assistant: {\"response\": \"No\"}\n\n"

        "User: Is it a bird?\n"
        "Assistant: {\"response\": \"Yes\"}\n\n"

        "Hidden word: Carrot\n"
        "User: Is it a fruit?\n"
        "Assistant: {\"response\": \"No\"}\n\n"

        "User: Is it food?\n"
        "Assistant: {\"response\": \"Yes\"}"
    )
)

agent = create_agent(
    model=model,
    system_prompt=system_prompt,
    response_format=GuessAnswer   
)

def load_agent():
    return agent
