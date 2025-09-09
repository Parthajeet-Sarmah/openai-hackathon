from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
# Absolute imports by package
from ai_inference.prompt_builder import build_summary_prompt
from ai_inference.model_inference import InferenceEngine
from ai_inference.event_fetcher import EventFetcher

app = FastAPI()
engine = InferenceEngine()
event_fetcher = EventFetcher("events.db")

class InferenceRequest(BaseModel):
    event_type: str = ""
    summary_type: str = "daily"
    max_events: int = 100

@app.post("/summarize")
def summarize(req: InferenceRequest):

    print(req.event_type)
    print(req.max_events)

    events = event_fetcher.fetch_recent_events(event_type=req.event_type, limit=req.max_events)

    if(len(events) <= 0):
        return Response("**No new events have occured as of now!** \n\n", status_code=200)

    prompt = build_summary_prompt(events, summary_type=req.summary_type)
    tokens_generator = engine.run(prompt, stream=True)
    return StreamingResponse(tokens_generator, media_type="text/plain")

