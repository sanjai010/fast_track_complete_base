"""
Improved API server, kept separate from the original ``src.api_server``.

Run with:

    uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001
"""

from __future__ import annotations

import os
import re
import traceback
import uuid
from copy import deepcopy

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.step6_ingest_qdrant import get_client
from src.step8_business_rules import apply_business_rules
from .hybrid_search import hybrid_retrieve
from src.step9_gemini import (
    generate_response,
    generate_multi_intent_response,
)
from src.step10_validate import validate_response

from .support_routing import (
    helpful_unknown_response,
    route_post_service_issue,
    suggested_actions,
)

from .candidate_analysis import (
    inspect_candidates,
    combine_intent_evidence,
)

from .intent_signals import detect_intent_signals

from .multi_intent_decision import (
    build_multi_intent_decision,
)

from .conversation_router import route_basic_conversation

from .knowledge_lookup import lookup_by_intent, record_as_result

from .follow_up import (
    build_conversation_state,
    resolve_follow_up,
)

from .conversation_memory import (
    new_session_id,
    record_turn,
    set_thread_type,
)

from .booking_store import (
    list_bookings,
    save_booking,
)


# ---------------------------------------------------------
# Conversation context builder
# ---------------------------------------------------------

def build_context_query(
    message: str,
    history: list[dict],
) -> str:
    """
    Build a context-aware search query by combining the current
    message with relevant conversation history.

    For follow-up questions like "what about the other one?" or
    "how much does that cost?", this extracts the subject from
    prior turns so retrieval can find the right knowledge.
    """

    if not history:
        return message

    # Extract the last few meaningful exchanges
    recent = history[-6:]

    # Build a context summary from recent conversation
    context_parts = []
    for turn in recent:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "user":
            context_parts.append(f"Customer asked: {content}")
        elif role == "assistant":
            # Keep assistant responses short for context
            short = content[:150] + "..." if len(content) > 150 else content
            context_parts.append(f"Agent answered: {short}")

    context_summary = " | ".join(context_parts)

    # Combine context with current message for better retrieval
    expanded_query = (
        f"{message} "
        f"(Conversation context: {context_summary})"
    )

    return expanded_query


# ---------------------------------------------------------
# Best-result selection
# ---------------------------------------------------------

# When a message carries several explicit signals, the most specific
# closing intent wins: a price question must resolve to PRICE even when
# "what is" also fired the broad DISCOVERY signal.
INTENT_PRIORITY = [
    "PRICE",
    "CUSTOM_QUOTE",
    "DISCOUNT",
    "BOOKING",
    "AVAILABILITY",
    "DURATION",
    "COMPATIBILITY",
    "WARRANTY",
    "LEGAL",
    "SAFETY",
    "PAYMENT",
    "AFTERCARE",
    "COMPLAINT",
    "OPTIONS",
    "PROCESS",
    "PREPARATION",
    "COMBINATION",
    "REQUEST",
    "PROBLEM_NEED",
    "FEATURES",
    "DISCOVERY",
]


def _prioritise(intents: list[str]) -> list[str]:
    def rank(intent: str) -> tuple[int, str]:
        intent = str(intent).upper()
        if intent in INTENT_PRIORITY:
            return (INTENT_PRIORITY.index(intent), intent)
        return (len(INTENT_PRIORITY), intent)

    return sorted(intents, key=rank)


def select_best_result(
    results: list[dict],
    supported_intents: list[dict],
    explicit_intents: list[str],
) -> dict | None:
    """Pick the retrieval result that matches what the customer asked.

    Priority:
    1. The most specific explicit signal, resolved either through
       retrieval support or an exact service + intent knowledge lookup
       ("how much is PPF" -> the PRICE record, not rank-0 COMPATIBILITY).
    2. The highest-scoring candidate that passes Step 8.
    3. The rank-0 fused result.
    """

    supported_by_intent = {
        str(item.get("intent") or "").upper(): item
        for item in supported_intents
    }

    service_context = ""
    if results:
        best_by_score = max(
            results,
            key=lambda item: float(item.get("score", 0.0)),
        )
        service_context = str(best_by_score.get("service") or "")

    for intent in _prioritise(explicit_intents):
        intent = str(intent).upper()

        # 1a. Retrieval surfaced this explicit intent.
        if intent in supported_by_intent:
            return supported_by_intent[intent]["result"]

        # 1b. Vector rank missed it; resolve the exact canonical record.
        record = lookup_by_intent(service_context, intent)
        if record:
            return record_as_result(record)

    # 2. No usable signal: first candidate Step 8 accepts.
    if explicit_intents:
        ranked = sorted(
            results,
            key=lambda item: float(item.get("score", 0.0)),
            reverse=True,
        )
        for candidate in ranked:
            if apply_business_rules(candidate).decision != "NOT_CONFIRMED":
                return candidate

    # 3. Fall back to the fused rank-0 result (Step 8 still gates it).
    return results[0] if results else None


app = FastAPI(
    title="FastTracks Car Care AI - Enhanced MVP",
    description="Original RAG pipeline with safe intent-aware support routing.",
    version="1.2.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[dict] = Field(default_factory=list)
    session_id: str | None = None


class EnhancedChatResponse(BaseModel):
    response: str
    decision: str
    validated: bool
    route: str
    suggested_actions: list[str]
    session_id: str | None = None
    canonical_id: str | None = None
    retrieval_score: float | None = None


class BookingRequest(BaseModel):
    date: str = Field(min_length=1, max_length=20)
    time: str = Field(min_length=1, max_length=30)
    service: str = Field(min_length=1, max_length=200)
    vehicle: str = Field(default="", max_length=200)
    name: str = Field(default="", max_length=200)
    phone: str = Field(default="", max_length=40)


# ---------------------------------------------------------
# Qdrant
# ---------------------------------------------------------

qdrant_client = None


@app.on_event("startup")
def startup_event() -> None:
    global qdrant_client
    qdrant_client = get_client()


@app.on_event("shutdown")
def shutdown_event() -> None:
    if qdrant_client is not None:
        qdrant_client.close()


# ---------------------------------------------------------
# General FastTracks service catalogue
# ---------------------------------------------------------

FASTTRACKS_SERVICES = [
    "Alloy Wheel Upgrades",
    "Ambient Lighting",
    "Bespoke Paint Jobs",
    "Body Kits / Conversion Kits",
    "Car Detailing",
    "Car Spa",
    "Ceramic Coating",
    "Custom Audio",
    "Custom Grilles",
    "Dashcams & Parking Sensors",
    "Deep Interior Cleaning",
    "FastTracks Studio",
    "Hydro Dipping",
    "Infotainment Upgrades",
    "Interior Customization",
    "Luxury Recliners",
    "Other Custom Work",
    "PPF",
    "Roll Cages",
    "Roof-Lining Conversions",
    "SRS Paint Correction",
    "Spoilers / Aero Kits",
    "Suspension Modifications",
    "Track-Day Preparation",
    "Undercarriage Protection",
    "Vinyl Wrapping",
    "Window Tinting",
]


def is_general_services_question(message: str) -> bool:
    """
    Detect broad questions asking what FastTracks offers.

    This is intentionally narrow so that service-specific
    questions continue through normal RAG retrieval.
    """

    text = message.lower().strip()

    patterns = [
        r"\bwhat services do you offer\b",
        r"\bwhat services do you provide\b",
        r"\bwhat services are available\b",
        r"\bwhat can you do\b",
        r"\bwhat do you guys do\b",
        r"\bwhat can i get done\b",
        r"\bwhat all services do you have\b",
        r"\blist your services\b",
        r"\bshow me your services\b",
        r"\bservices you offer\b",
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def general_services_response() -> str:
    """
    Customer-facing service catalogue.

    No internal intent, retrieval, model, or business-rule
    terminology is exposed.
    """

    services = "\n".join(
        f"  • {service}"
        for service in FASTTRACKS_SERVICES
    )

    return (
        "FastTracks is a premium car customization and detailing studio "
        "offering a wide range of services, including:\n\n"
        f"{services}\n\n"
        "Whether you're looking to enhance your car's appearance, protect "
        "its paint, or upgrade the interior, we have a service for you. "
        "Tell me what you'd like to do with your car, and I'll guide you "
        "to the right service."
    )


# ---------------------------------------------------------
# Customer-safe knowledge cleanup
# ---------------------------------------------------------

def customer_safe_answer(answer: str) -> str:
    """
    Keep the approved wording untouched in meaning, but remove internal
    workflow terminology before the content reaches the response model.
    """

    # Internal workflow terminology
    answer = re.sub(
        r"\s*\(\s*ENQUIRY\s*/\s*VERIFY\s*\)",
        "",
        answer or "",
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"\s*\(\s*ENQUIRY\s*/\s*CONFIRM\s*\)",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    # Make internal wording customer-facing
    answer = re.sub(
        r"\bNOT CONFIRMED as a universal duration\b",
        "There is no confirmed universal duration",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"\bNOT CONFIRMED\b",
        "not confirmed",
        answer,
        flags=re.IGNORECASE,
    )

    return answer.strip()


def make_customer_safe_knowledge(items: list[dict]) -> list[dict]:
    """
    Keep the original approved knowledge untouched in meaning, but remove
    internal workflow terminology before sending the content
    to the response-generation model.
    """

    safe_items = deepcopy(items)

    for item in safe_items:
        item["approved_answer"] = customer_safe_answer(
            str(item.get("approved_answer") or "")
        )
        variants = item.get("approved_answer_variants", []) or []
        item["approved_answer_variants"] = [
            customer_safe_answer(str(v)) for v in variants
        ]

    return safe_items


def clean_generated_response(response: str) -> str:
    """
    Final protection against internal implementation terms
    accidentally appearing in a customer response.
    """

    if not response:
        return response

    cleaned = response

    replacements = {
        "ENQUIRY / VERIFY": "",
        "ENQUIRY/VERIFY": "",
        "ENQUIRY / CONFIRM": "",
        "ENQUIRY/CONFIRM": "",
        "APPROVED ANSWER:": "",
        "FINAL ACTION:": "",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # Customer-facing wording for internal status terms that may leak
    # from an approved answer into the generated text.
    cleaned = re.sub(
        r"\bNOT CONFIRMED as a universal duration\b",
        "There is no confirmed universal duration",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bNOT CONFIRMED\b",
        "not confirmed",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove excessive blank lines created by replacements
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root() -> dict:
    return {
        "service": "FastTracks Enhanced MVP",
        "docs": "/docs",
        "status": "ok",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "FastTracks Enhanced MVP",
    }


# ---------------------------------------------------------
# Chat
# ---------------------------------------------------------

@app.post("/chat", response_model=EnhancedChatResponse)
def chat(request: ChatRequest) -> EnhancedChatResponse:

    message = request.message.strip()
    history = request.history or []
    session_id = request.session_id or new_session_id()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # -----------------------------------------------------
    # Basic conversation
    # -----------------------------------------------------

    conversation = route_basic_conversation(message)

    if conversation:
        return EnhancedChatResponse(
            response=conversation.response,
            decision="CONVERSATION",
            validated=True,
            route=conversation.route,
            suggested_actions=[],
            session_id=session_id,
            canonical_id=None,
            retrieval_score=None,
        )

    # -----------------------------------------------------
    # General service discovery
    # -----------------------------------------------------
    #
    # Handle broad questions directly instead of allowing
    # weak vector matches to produce an unrelated answer.
    #

    if is_general_services_question(message):
        return EnhancedChatResponse(
            response=general_services_response(),
            decision="DISCOVERY",
            validated=True,
            route="RAG",
            suggested_actions=suggested_actions("RAG"),
            session_id=session_id,
            canonical_id="GENERAL_DISCOVERY",
            retrieval_score=1.0,
        )

    # -----------------------------------------------------
    # Post-service / complaint routing
    # -----------------------------------------------------

    support_route = route_post_service_issue(message)

    if support_route:
        # Keep the thread in complaint mode so follow-ups ("and the
        # warranty?") stay inside the complaint guardrails.
        set_thread_type(session_id, "COMPLAINT")

        record_turn(
            session_id,
            service=None,
            intent="COMPLAINT",
            canonical_id=support_route.canonical_id,
            approved_answer=support_route.response,
            score=0.0,
            decision=support_route.decision,
            message=message,
        )

        return EnhancedChatResponse(
            response=support_route.response,
            decision=support_route.decision,
            validated=True,
            route=support_route.name,
            suggested_actions=suggested_actions(
                support_route.name
            ),
            session_id=session_id,
            canonical_id=support_route.canonical_id,
        )

    try:

        # -------------------------------------------------
        # Step 7 - Retrieve top candidates
        # -------------------------------------------------

        # -------------------------------------------------
        # Follow-up / conversation memory
        #
        # If this message is a follow-up ("what about the other one?",
        # "and the warranty?"), resolve its referent against the last
        # topic and build a self-contained retrieval query.
        # -------------------------------------------------

        follow_up = resolve_follow_up(
            message,
            session_id,
            history,
        )

        if follow_up:
            search_query = follow_up["resolved_query"]
            conversation_state = build_conversation_state(
                follow_up["referent"]
            )
            print(
                "\n========== FOLLOW-UP RESOLVED =========="
                f"\nmessage          : {message}"
                f"\nresolved query   : {search_query}"
                f"\nsource           : {follow_up['rewrite_source']}"
                f"\nreferent service : {follow_up['referent'].get('service')}"
                f"\nreferent intent  : {follow_up['referent'].get('intent')}"
                "\n=========================================\n"
            )
        else:
            # Build a context-aware query for follow-up questions
            search_query = build_context_query(message, history)
            conversation_state = None

        results = hybrid_retrieve(
            search_query,
            top_k=30,
            client=qdrant_client,
        )
        print("\n========== RAW RETRIEVAL ==========")

        for r in results:
            if r.get("canonical_id") in [
                "EXT-01_PRICE",
                "EXT-01_DURATION",
            ]:
                print("CANONICAL ID:", r.get("canonical_id"))
                print("APPROVED ANSWER:", repr(r.get("approved_answer")))
                print("FULL RESULT:", r)

        print("===================================\n")

        inspect_candidates(results)

        if not results:
            return EnhancedChatResponse(
                response=helpful_unknown_response(),
                decision="NOT_CONFIRMED",
                validated=True,
                route="HELPFUL_FALLBACK",
                suggested_actions=suggested_actions(
                    "HELPFUL_FALLBACK"
                ),
                session_id=session_id,
            )

        # -------------------------------------------------
        # Step 7.5 - Detect explicit customer intents
        # -------------------------------------------------

        signals = detect_intent_signals(message)

        explicit_intents = list(signals.keys())

        print("\n" + "=" * 70)
        print("INTENT SIGNALS")
        print("=" * 70)
        print("Message:", message)
        print("Explicit intents:", explicit_intents)

        # -------------------------------------------------
        # Step 7.6 - Combine explicit intent + retrieval
        # -------------------------------------------------

        combined = combine_intent_evidence(
            results,
            explicit_intents,
        )

        print("\nSUPPORTED INTENTS:")

        for item in combined["supported_intents"]:
            print(
                f"  {item['intent']} -> "
                f"{item['canonical_id']} -> "
                f"{item['service']} -> "
                f"{item['score']:.4f}"
            )

        # -------------------------------------------------
        # Multi-intent path
        # -------------------------------------------------

        if len(combined["supported_intents"]) > 1:

            print("\n" + "=" * 70)
            print("MULTI-INTENT REQUEST")
            print("=" * 70)

            # Apply Step 8 rules independently
            # to every supported intent.

            multi_decision = build_multi_intent_decision(
                combined["supported_intents"]
            )

            # -------------------------------------------------
            # Customer-safe knowledge
            # -------------------------------------------------

            combined_knowledge = make_customer_safe_knowledge(
                multi_decision["decisions"]
            )

            print("\nCOMBINED CUSTOMER-SAFE KNOWLEDGE:")

            for item in combined_knowledge:
                print(
                    f"\n  INTENT: {item['intent']}"
                    f"\n  SERVICE: {item['service']}"
                    f"\n  CANONICAL ID: {item['canonical_id']}"
                    f"\n  APPROVED ANSWER: "
                    f"{item['approved_answer']}"
                )

# -------------------------------------------------
            # Step 9 - Generate one response for all intents
            # -------------------------------------------------

            generated_response = generate_multi_intent_response(
                message,
                combined_knowledge,
                history=history,
                conversation_state=conversation_state,
            )

            print("\n========== STEP 9 MULTI-INTENT OUTPUT ==========")
            print(generated_response)
            print("===============================================\n")

            generated_response = clean_generated_response(
                generated_response
            )

            # -------------------------------------------------
            # Step 10 - Validate
            # -------------------------------------------------

            strongest_item = max(
                combined["supported_intents"],
                key=lambda item: item["score"],
            )

            strongest_decision = None

            for item in multi_decision["decisions"]:
                if (
                    item["canonical_id"]
                    == strongest_item["canonical_id"]
                ):
                    strongest_decision = item["decision"]
                    break

            if strongest_decision is not None:
                (
                    validated,
                    final_response,
                    _reason,
                ) = validate_response(
                    generated_response,
                    strongest_decision,
                )
            else:
                validated = True
                final_response = generated_response

            final_response = clean_generated_response(
                final_response
            )

            highest_score = strongest_item["score"]

            # Remember the topic the customer asked about, so later
            # follow-ups can resolve their pronouns against it.
            record_turn(
                session_id,
                service=strongest_item.get("service"),
                intent=strongest_item.get("intent"),
                canonical_id=strongest_item.get("canonical_id"),
                approved_answer=final_response,
                score=highest_score,
                decision="MULTI_INTENT",
                message=message,
            )

            return EnhancedChatResponse(
                response=final_response,
                decision="MULTI_INTENT",
                validated=validated,
                route="RAG",
                suggested_actions=suggested_actions("RAG"),
                session_id=session_id,
                canonical_id="MULTI",
                retrieval_score=highest_score,
            )

        # -------------------------------------------------
        # Single-intent path
        #
        # Select the result that matches the customer's explicit
        # wording (not merely the fused rank-0 candidate).
        # -------------------------------------------------

        best_result = select_best_result(
            results,
            combined["supported_intents"],
            explicit_intents,
        )

        if best_result is None:
            return EnhancedChatResponse(
                response=helpful_unknown_response(),
                decision="NOT_CONFIRMED",
                validated=True,
                route="HELPFUL_FALLBACK",
                suggested_actions=suggested_actions(
                    "HELPFUL_FALLBACK"
                ),
                session_id=session_id,
            )

        decision = apply_business_rules(
            best_result
        )

        # Single path also strips internal wording from the approved
        # answer before it reaches the prompt or the customer.
        if decision.approved_answer:
            decision.approved_answer = customer_safe_answer(
                decision.approved_answer
            )

        # -------------------------------------------------
        # Confidence fallback
        # -------------------------------------------------

        if decision.decision == "NOT_CONFIRMED":
            return EnhancedChatResponse(
                response=helpful_unknown_response(),
                decision=decision.decision,
                validated=True,
                route="HELPFUL_FALLBACK",
                suggested_actions=suggested_actions(
                    "HELPFUL_FALLBACK"
                ),
                session_id=session_id,
                canonical_id=decision.canonical_id,
                retrieval_score=decision.score,
            )

        # -------------------------------------------------
        # Step 9 - Response generation
        # -------------------------------------------------

        generated_response = generate_response(
            message,
            decision,
            history=history,
            conversation_state=conversation_state,
        )

        generated_response = clean_generated_response(
            generated_response
        )

        # -------------------------------------------------
        # Step 10 - Validate
        # -------------------------------------------------

        validated, final_response, _reason = validate_response(
            generated_response,
            decision,
        )

        final_response = clean_generated_response(
            final_response
        )

        # Remember the resolved topic so later follow-ups resolve
        # against it.
        record_turn(
            session_id,
            service=decision.service,
            intent=decision.intent,
            canonical_id=decision.canonical_id,
            approved_answer=decision.approved_answer or final_response,
            score=decision.score,
            decision=decision.decision,
            message=message,
        )

        return EnhancedChatResponse(
            response=final_response,
            decision=decision.decision,
            validated=validated,
            route="RAG",
            suggested_actions=suggested_actions("RAG"),
            session_id=session_id,
            canonical_id=decision.canonical_id,
            retrieval_score=decision.score,
        )

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="The chat service could not process the request.",
        )


# ---------------------------------------------------------------
# Booking storage
# ---------------------------------------------------------------


@app.post("/bookings")
def create_booking(request: BookingRequest) -> dict:
    record = {
        "date": request.date,
        "time": request.time,
        "service": request.service,
        "vehicle": request.vehicle,
        "name": request.name,
        "phone": request.phone,
    }

    try:
        stored = save_booking(record)
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="The booking could not be saved.",
        )

    return {
        "status": "confirmed",
        "reference": stored["id"],
        "booking": stored,
    }


@app.get("/bookings")
def get_bookings(date: str | None = None) -> dict:
    try:
        records = list_bookings(date)
    except Exception:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="The bookings could not be read.",
        )

    return {
        "count": len(records),
        "bookings": records,
    }