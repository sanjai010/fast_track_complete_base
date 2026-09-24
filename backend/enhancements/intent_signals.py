"""
Intent signal detection.

This layer detects explicit customer intent signals before
retrieval evidence is combined.

It is intentionally lightweight and deterministic.

The RAG system still requires retrieval evidence before an
intent is considered supported.
"""

from __future__ import annotations

import re


INTENT_PATTERNS = {

    # ---------------------------------------------------------
    # DISCOVERY
    # ---------------------------------------------------------
    "DISCOVERY": [
        r"\bwhat services\b",
        r"\bwhat service\b",
        r"\bwhat all services\b",
        r"\bwhat do you guys do\b",
        r"\bwhat do u guys do\b",
        r"\bwhat do you do\b",
        r"\bwhat do u do\b",
        r"\bwhat do you offer\b",
        r"\bwhat do u offer\b",
        r"\bwhat all do you offer\b",
        r"\bwhat all do u offer\b",
        r"\bwhat services do you provide\b",
        r"\bwhat services do u provide\b",
        r"\bwhat services you provide\b",
        r"\bwhat service you provide\b",
        r"\bwhat services you have\b",
        r"\bwhat services u have\b",
        r"\bwhat service u have\b",
        r"\bwhat do you guys provide\b",
        r"\bwhat do u guys provide\b",
        r"\bdo you guys do\b",
        r"\bdo u guys do\b",
        r"\bdo you do\b",
        r"\bdo u do\b",
        r"\btell me about\b",
        r"\bwhat is\b",
        r"\bwhat exactly is\b",
        r"\binterested in\b",
        r"\bwhat can you do\b",
        r"\bwhat can u do\b",
    ],

    # ---------------------------------------------------------
    # PRICE
    # ---------------------------------------------------------
    "PRICE": [
        r"\bhow much\b",
        r"\bhow much does\b",
        r"\bhow much will\b",
        r"\bhow much for\b",
        r"\bcost\b",
        r"\bprice\b",
        r"\bpricing\b",
        r"\bstarting price\b",
        r"\bcost roughly\b",
        r"\broughly how much\b",
        r"\bwhat will .* cost\b",
    ],

    # ---------------------------------------------------------
    # DURATION
    # ---------------------------------------------------------
    "DURATION": [
        r"\bhow long\b",
        r"\bhow many days\b",
        r"\bhow many hours\b",
        r"\bduration\b",
        r"\bwhen will .* be ready\b",
        r"\bhow long will\b",
        r"\bhow much time\b",
        r"\bhow many day\b",
        r"\bin one day\b",
        r"\btake to complete\b",
        r"\btake to finish\b",
        r"\bhow long .* take\b",
    ],

    # ---------------------------------------------------------
    # PROCESS
    # ---------------------------------------------------------
    "PROCESS": [
        r"\bhow is .* done\b",
        r"\bwhat is the process\b",
        r"\bhow do you .* carry out\b",
        r"\bwhat are the steps\b",
        r"\bprocedure\b",
        r"\bhow does .* work\b",
        r"\bhow do .* work\b",
        r"\bwhat happens\b",
        r"\bwhat's involved\b",
        r"\bwhats involved\b",
    ],

    # ---------------------------------------------------------
    # OPTIONS
    # ---------------------------------------------------------
    "OPTIONS": [
        r"\bwhat options\b",
        r"\bwhat .* options\b",
        r"\bvariants\b",
        r"\bwhich .* options\b",
        r"\bdifferent types\b",
        r"\bchoices\b",
        r"\bwhat choices\b",
        r"\bwhat can i choose\b",
        r"\bwhat can we choose\b",
    ],

    # ---------------------------------------------------------
    # BOOKING
    # ---------------------------------------------------------
    "BOOKING": [
        r"\bbook\b",
        r"\bbooking\b",
        r"\bschedule\b",
        r"\bscheduling\b",
        r"\bbook a slot\b",
        r"\bget a slot\b",
        r"\breserve\b",
        r"\breservation\b",
        r"\bi want to get .* done\b",
        r"\bi want to do\b",
    ],

    # ---------------------------------------------------------
    # AVAILABILITY
    # ---------------------------------------------------------
"AVAILABILITY": [
    r"\bavailability\b",
    r"\bany slot\b",
    r"\bany slots\b",
    r"\bslot today\b",
    r"\bslot tomorrow\b",
    r"\bslots today\b",
    r"\bslots tomorrow\b",
    r"\bthis weekend\b",
    r"\btomorrow\b",
    r"\btoday\b",
    r"\bthis week\b",
    r"\bthis sunday\b",
    r"\bopen today\b",
    r"\bopen tomorrow\b",
    r"\bwhen can i come\b",
    r"\bwhen can i bring\b",
    r"\bcan i come\b",
    r"\bcan i bring\b",
    r"\bcan you fit me in\b",
    r"\bdo you have a slot\b",
    r"\bdo you have any slot\b",
    r"\bdo you have availability\b",
],
    # ---------------------------------------------------------
    # COMPATIBILITY
    # ---------------------------------------------------------
    "COMPATIBILITY": [
        r"\bcompatible\b",
        r"\bcompatibility\b",
        r"\bwill .* fit\b",
        r"\bfit my\b",
        r"\bfit on my\b",
        r"\bwork on my\b",
        r"\bpossible for my\b",
        r"\bcan you do .* on my\b",
        r"\bcan u do .* on my\b",
    ],

    # ---------------------------------------------------------
    # WARRANTY
    # ---------------------------------------------------------
    "WARRANTY": [
        r"\bwarranty\b",
        r"\bguarantee\b",
        r"\bcovered under warranty\b",
        r"\bhow long is the warranty\b",
        r"\bwhat warranty\b",
        r"\bwarranty period\b",
    ],

    # ---------------------------------------------------------
    # CUSTOM QUOTE
    # ---------------------------------------------------------
    "CUSTOM_QUOTE": [
        r"\bexact quote\b",
        r"\bexact price\b",
        r"\bfinal price\b",
        r"\bquotation\b",
        r"\bquote for my car\b",
        r"\bquote for my vehicle\b",
        r"\bcustom quote\b",
        r"\bpersonalized quote\b",
        r"\bwhat would .* cost on my\b",
    ],

    # ---------------------------------------------------------
    # DISCOUNT
    # ---------------------------------------------------------
    "DISCOUNT": [
        r"\bdiscount\b",
        r"\boffer\b",
        r"\bbetter price\b",
        r"\breduce the price\b",
        r"\bprice reduction\b",
        r"\bscheme\b",
        r"\bfestival offer\b",
        r"\bdeal\b",
        r"\bany offer\b",
    ],

    # ---------------------------------------------------------
    # PROBLEM / NEED
    # ---------------------------------------------------------
    "PROBLEM_NEED": [
        r"\bwill .* solve my problem\b",
        r"\bwill .* help\b",
        r"\bcan .* fix\b",
        r"\bfix my problem\b",
        r"\bi have a problem\b",
        r"\bmy car has a problem\b",
        r"\bwhich service do i need\b",
        r"\bwhich service should i get\b",
        r"\bwhat should i get\b",
        r"\bis .* right for me\b",
    ],

    # ---------------------------------------------------------
    # FEATURES
    # ---------------------------------------------------------
    "FEATURES": [
        r"\bfeatures\b",
        r"\bbenefits\b",
        r"\bwhat do i get with\b",
        r"\bwhat makes .* useful\b",
        r"\bwhat is special about\b",
        r"\badvantages\b",
        r"\bwhat does .* offer\b",
    ],

    # ---------------------------------------------------------
    # COMBINATION
    # ---------------------------------------------------------
    "COMBINATION": [
        r"\btogether with\b",
        r"\bcombine\b",
        r"\bcombined package\b",
        r"\balong with\b",
        r"\bwith another service\b",
        r"\bdo .* and .* together\b",
        r"\bboth .* and\b",
    ],

    # ---------------------------------------------------------
    # PAYMENT
    # ---------------------------------------------------------
    "PAYMENT": [
        r"\bpayment\b",
        r"\bpay\b",
        r"\bhow do i pay\b",
        r"\bpayment methods\b",
        r"\bpay by card\b",
        r"\bcard payment\b",
        r"\bupi\b",
        r"\bemi\b",
        r"\binstallment\b",
    ],

    # ---------------------------------------------------------
    # PREPARATION
    # ---------------------------------------------------------
    "PREPARATION": [
        r"\bbefore bringing\b",
        r"\bbefore i bring\b",
        r"\bprepare\b",
        r"\bpreparation\b",
        r"\bwhat should i do before\b",
        r"\bwhat do i need to do before\b",
        r"\bwhat do you need from me\b",
    ],

    # ---------------------------------------------------------
    # AFTERCARE
    # ---------------------------------------------------------
    "AFTERCARE": [
        r"\baftercare\b",
        r"\bafter care\b",
        r"\bhow do i maintain\b",
        r"\bhow should i care\b",
        r"\bhow do i take care\b",
        r"\bafter the service\b",
        r"\bafter getting\b",
        r"\bmaintain\b",
    ],

    # ---------------------------------------------------------
    # SAFETY
    # ---------------------------------------------------------
    "SAFETY": [
        r"\bis .* safe\b",
        r"\bsafe\b",
        r"\brisky\b",
        r"\brisk\b",
        r"\bsafety\b",
        r"\bany safety issue\b",
        r"\bwill .* damage\b",
        r"\bcause any problem\b",
    ],

    # ---------------------------------------------------------
    # LEGAL
    # ---------------------------------------------------------
    "LEGAL": [
        r"\bis .* legal\b",
        r"\blegal\b",
        r"\ballowed by rto\b",
        r"\brto approval\b",
        r"\bpolice issue\b",
        r"\blegal in india\b",
        r"\broad legal\b",
    ],

    # ---------------------------------------------------------
    # COMPLAINT
    # ---------------------------------------------------------
    "COMPLAINT": [
        r"\bcomplaint\b",
        r"\bsomething went wrong\b",
        r"\bproblem after\b",
        r"\bnot working\b",
        r"\bwork is not correct\b",
        r"\bnot happy with\b",
        r"\bissue after\b",
        r"\bproblem with the service\b",
    ],

    # ---------------------------------------------------------
    # REQUEST
    # ---------------------------------------------------------
    "REQUEST": [
        r"\bi want to get\b",
        r"\bi want .* installed\b",
        r"\bcan you install\b",
        r"\bcan u install\b",
        r"\bplease get .* done\b",
        r"\bi need .* done\b",
        r"\bwant to get .* done\b",
    ],
}


def detect_intent_signals(message: str) -> dict[str, list[str]]:
    """
    Detect explicit intent signals.

    Multiple intents may be returned for a single message.
    Retrieval evidence is still required before an intent
    becomes supported.
    """

    text = message.lower().strip()

    detected: dict[str, list[str]] = {}

    for intent, patterns in INTENT_PATTERNS.items():
        matches = []

        for pattern in patterns:
            if re.search(pattern, text):
                matches.append(pattern)

        if matches:
            detected[intent] = matches

    return detected