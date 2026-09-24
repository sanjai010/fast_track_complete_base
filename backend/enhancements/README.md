# Enhanced MVP layer

This folder is separate from `src/` and never writes to either company
dataset in `data/raw/`. The original API remains available and unchanged.

## What changed

- Detects post-service issues before vector retrieval.
- Recognizes a named service, for example "ceramic coating", and uses that
  service's existing approved complaint answer.
- If no service is named, asks for the service, vehicle, date, and issue
  details instead of guessing.
- Replaces the unhelpful generic unsupported-question message with a short
  guide to the bot's supported topics.
- Adds `route`, `canonical_id`, `retrieval_score`, and `suggested_actions`
  fields for a frontend to use. Existing clients can still simply display
  `response`.

## Run tests

Stop any running server first, then run:

```powershell
python -m unittest enhancements.test_support_routing
```

## Start the enhanced server

The original server uses port 8000. Run the enhanced one on port 8001:

```powershell
uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001
```

Open `http://127.0.0.1:8001/docs` and test:

```json
{
  "message": "I got ceramic coating two days ago and I have an issue. Please check it again."
}
```

The expected decision is `ESCALATE_COMPLAINT`; no vector-score guess is
needed for this safety-sensitive route.

## Frontend quick actions

Use the `suggested_actions` list returned by `/chat` to render buttons such
as `Book a service` or `Post-service support`. No frontend source exists in
this repository, so this folder provides the API contract rather than a UI.
