from jinja2 import Template

def build_summary_prompt(events, summary_type="daily"):
    event_lines = []
    for ts, source, event, data in events:
        event_lines.append(f"{source.upper()}: {event} ({data}) at {ts}")
    joined = "\n".join(event_lines)
    prompt = f"Summarize the following user activity ({summary_type}):\n{joined}\nSummary:"
    return prompt
