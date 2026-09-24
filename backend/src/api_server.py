"""
FastTracks Car Care AI Backend
MVP FastAPI Server

Flow:
Customer
   ↓
Step 7 - Retrieval
   ↓
Step 8 - Business Rules
   ↓
Step 9 - Gemini
   ↓
Step 10 - Response Validation
   ↓
API Response
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .step6_ingest_qdrant import get_client
from .step7_retrieve import retrieve
from .step8_business_rules import apply_business_rules
from .step9_gemini import generate_response
from .step10_validate import validate_response


app = FastAPI(
    title="FastTracks Car Care AI",
    description="AI customer support backend for FastTracks Car Care",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
# MVP setting: allow the frontend to connect.
# Later, restrict this to the actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    decision: str
    validated: bool


# ---------------------------------------------------------
# Qdrant client
# ---------------------------------------------------------

qdrant_client = None


@app.on_event("startup")
def startup_event():
    global qdrant_client
    qdrant_client = get_client()


@app.on_event("shutdown")
def shutdown_event():
    global qdrant_client

    if qdrant_client is not None:
        try:
            qdrant_client.close()
        except Exception:
            pass


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FastTracks Car Care AI",
    }


# ---------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        # Step 7 — Retrieval
        results = retrieve(
            message,
            top_k=3,
            client=qdrant_client,
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No knowledge result found.",
            )

        best_result = results[0]

        # Step 8 — Business rules
        decision = apply_business_rules(best_result)

        # Step 9 — Gemini / approved response
        generated_response = generate_response(
            message,
            decision,
        )

        # Step 10 — Response validation
        validated, final_response, reason = validate_response(
            generated_response,
            decision,
        )

        return ChatResponse(
            response=final_response,
            decision=decision.decision,
            validated=validated,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(exc)}",
        )