"""NyxOS Local AI Assistant — interface.

Real local model integration comes later (llama.cpp / ollama).
This stub provides the API and deterministic fallbacks.
"""


class Assistant:
    def __init__(self, model=None):
        self.model = model

    def explain_tool(self, tool_name):
        return {"tool": tool_name, "note": "Local AI model not loaded yet."}

    def explain_output(self, tool_name, output):
        return {"tool": tool_name, "summary": output[:300] if output else ""}

    def suggest_next(self, context):
        return {"suggestions": []}
