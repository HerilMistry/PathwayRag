# integrations/mistral_client.py
"""MistralClient wrapper providing .invoke() interface"""

import os
import requests
from typing import Any, Optional

# Import Runnable base so the adapter can be used in langchain chains
try:
    from langchain_core.runnables.base import Runnable
except Exception:
    # Fallback import path for older langchain installs
    from langchain_core.runnables.base import Runnable  # type: ignore

class MistralClient:
    def __init__(self, endpoint: str = None, api_key: str = None):
        # Default to environment or a sensible localhost URL if not provided.
        # This avoids constructing requests to 'None' and gives a clear place
        # to run a local Mistral dev server for testing.
        self.endpoint = endpoint or os.getenv("MISTRAL_ENDPOINT") or "http://localhost:8000/v1/models/mistral-7b/infer"
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            print("[warning] MISTRAL_API_KEY not set; requests to the endpoint may fail with authentication errors.")

    def invoke(self, prompt: str, **params) -> str:
        """Invoke the Mistral endpoint with optional generation parameters.

        Any extra keyword args are placed inside a "parameters" field in the
        JSON payload so they can be used by different Mistral-style APIs.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"inputs": prompt}
        if params:
            payload["parameters"] = params

        resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # Support multiple response shapes
        return data.get("generated_text", data.get("output", data.get("text", "")))


class MistralLLM(Runnable):
    """A tiny Runnable-compatible adapter around MistralClient.

    This provides the minimal surface area CrewAI expects from an llm:
    - .model_name (string)
    - .callbacks (list or None)
    - .bind(...) from Runnable (inherited)
    - .invoke(input) that returns a string output
    """

    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None, model_name: str = "mistral-7b", callbacks: Optional[list] = None):
        self.client = MistralClient(endpoint=endpoint, api_key=api_key)
        self.model_name = model_name
        # CrewAI appends token handlers to llm.callbacks, so ensure it's a list
        self.callbacks = callbacks or []

    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs) -> Any:
        """Synchronous invoke called by langchain runnables.

        Accepts extra kwargs (like `stop`) and forwards them to the underlying
        MistralClient.invoke as generation parameters.
        """
        # Accept either a raw string or dicts produced by prompt.partial
        prompt = ""
        try:
            if isinstance(input, dict) and "input" in input:
                prompt = input["input"]
            else:
                prompt = str(input)
        except Exception:
            prompt = str(input)

        # Forward kwargs to the HTTP API as generation params
        return self.client.invoke(prompt, **kwargs)


def retrieve_knowledge(query: str, top_k: int = 3) -> str:
    """Simple retrieval wrapper that uses MistralClient to synthesize an answer.

    This function avoids importing agents to prevent circular imports. It expects
    a MistralClient instance to be provided by the caller if needed; for the
    tools in this repo we create a temporary client using environment variables.
    """
    import os

    # Lazy import to avoid heavy dependencies at module import time
    mc = MistralClient(endpoint=os.getenv("MISTRAL_ENDPOINT"))
    prompt = f"Answer the following question using the knowledge base context: {query}\nProvide a concise response."
    try:
        return mc.invoke(prompt)
    except Exception as e:
        return f"[retrieve_knowledge error] {e}"
