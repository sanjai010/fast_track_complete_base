# FastTracks Car Care - AI Chatbot

AI-powered customer support chatbot for FastTracks Car Care.

The project consists of:

- React + Vite frontend
- FastAPI backend
- RAG-based knowledge retrieval
- Local Qdrant vector database
- Intent detection and multi-intent handling
- Business rules and guardrails
- OpenRouter-based LLM response generation
- Response validation

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Prerequisites](#3-prerequisites)
4. [Clone the Repository](#4-clone-the-repository)
5. [Backend Setup](#5-backend-setup)
6. [Environment Variables](#6-environment-variables)
7. [Qdrant Setup](#7-qdrant-setup)
8. [Run the Backend](#8-run-the-backend)
9. [Frontend Setup](#9-frontend-setup)
10. [Run the Frontend](#10-run-the-frontend)
11. [Run the Complete Application](#11-run-the-complete-application)
12. [How the Chatbot Works](#12-how-the-chatbot-works)
13. [Git Workflow](#13-git-workflow)
14. [Pulling Latest Changes](#14-pulling-latest-changes)
15. [Installing Updated Dependencies](#15-installing-updated-dependencies)
16. [Environment and Secret Management](#16-environment-and-secret-management)
17. [Important Local Files](#17-important-local-files)
18. [Troubleshooting](#18-troubleshooting)
19. [Development Guidelines](#19-development-guidelines)
20. [Repository](#20-repository)

---

# 1. Project Overview

FastTracks Car Care AI Chatbot is a customer-facing assistant designed to answer questions about FastTracks Car Care services.

The system uses a RAG-based architecture where customer questions are matched against approved business knowledge before generating a response.

The system is designed to:

- Answer questions about available services
- Provide approved service information
- Handle pricing-related questions with guardrails
- Handle booking requests
- Handle availability requests
- Handle customer complaints and aftercare
- Handle multiple intents in a single customer message
- Avoid inventing unsupported business information
- Use an LLM only when appropriate
- Validate generated responses before returning them to the customer

---

# 2. Project Structure

```text
fast_track_complete_base/
│
├── README.md
├── .gitignore
│
├── backend/
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   ├── canonical_knowledge.json
│   │   │   └── questions.json
│   │   │
│   │   └── processed/
│   │       ├── step4_enriched_chunks.jsonl
│   │       └── step5_embeddings.npy
│   │
│   ├── enhancements/
│   │   ├── candidate_analysis.py
│   │   ├── conversation_router.py
│   │   ├── enhanced_api_server.py
│   │   ├── intent_signals.py
│   │   ├── multi_intent_decision.py
│   │   ├── query_normalizer.py
│   │   └── support_routing.py
│   │
│   ├── src/
│   │   ├── config.py
│   │   ├── step1_parse.py
│   │   ├── step2_clean.py
│   │   ├── step3_chunk.py
│   │   ├── step4_metadata.py
│   │   ├── step5_embed.py
│   │   ├── step6_ingest_qdrant.py
│   │   ├── step7_retrieve.py
│   │   ├── step8_business_rules.py
│   │   ├── step9_gemini.py
│   │   ├── step10_validate.py
│   │   └── ...
│   │
│   ├── requirements.txt
│   ├── README.md
│   └── .env
│
└── frontend/
    │
    ├── public/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── services/
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    ├── package-lock.json
    └── vite.config.js


================================================

