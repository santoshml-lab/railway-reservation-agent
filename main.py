from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import agent


# =========================
# APP
# =========================

app = FastAPI(
    title="Railway Reservation Agent",
    description=(
        "Agentic AI railway reservation assistant "
        "powered by Groq"
    ),
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# REQUEST MODEL
# =========================

class AgentRequest(BaseModel):
    goal: str


# =========================
# ROOT
# =========================

@app.get("/")
def root():

    return {
        "message": (
            "Railway Reservation Agent API "
            "is running 🚆🤖"
        )
    }


# =========================
# AGENT
# =========================

@app.post("/agent")
def run_agent(
    request: AgentRequest
):

    if not request.goal.strip():

        raise HTTPException(
            status_code=400,
            detail="Goal cannot be empty."
        )

    try:

        result = agent.run(
            request.goal
        )

        return {
            "goal": request.goal,
            "result": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
