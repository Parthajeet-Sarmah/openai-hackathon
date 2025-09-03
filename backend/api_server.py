from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
# Absolute imports by package
from ai_inference.event_fetcher import fetch_recent_events
from ai_inference.prompt_builder import build_summary_prompt
from ai_inference.model_inference import InferenceEngine

app = FastAPI()
engine = InferenceEngine()

class InferenceRequest(BaseModel):
    event_type: str = ""
    summary_type: str = "daily"
    max_events: int = 100

@app.post("/summarize")
def summarize(req: InferenceRequest):
    events = fetch_recent_events("events.db", event_type=req.event_type, limit=req.max_events)
    prompt = build_summary_prompt(events, summary_type=req.summary_type)
    tokens_generator = engine.run(prompt, stream=True)
    return StreamingResponse(tokens_generator, media_type="text/plain")

