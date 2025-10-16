# integrations/mistral_client.py
"""MistralClient wrapper providing .invoke() interface"""

import os
import requests

class MistralClient:
    def __init__(self, endpoint: str = None, api_key: str = None):
        self.endpoint = endpoint or os.getenv("MISTRAL_ENDPOINT")
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")

    def invoke(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"inputs": prompt}
        resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("generated_text", data.get("output", ""))

# main_agentic.py
"""ShopEase Agentic RAG System using MistralClient"""

import os
from dotenv import load_dotenv
from crewai import Crew, Process
from integrations.mistral_client import MistralClient

from intent_classifier.model import IntentClassifier, Intent
from tools.shopease_tools import (
    order_lookup_tool,
    refund_processor_tool,
    inventory_check_tool
)
from agents.crew_setup import create_agents, create_task
from integrations.mistral_client import retrieve_knowledge

# Load environment variables
load_dotenv()

# Initialize Mistral LLM client
llm = MistralClient(
    endpoint=os.getenv("MISTRAL_ENDPOINT")
)

# Initialize intent classifier (keyword-based fallback)
intent_classifier = IntentClassifier()

# Create agents with Mistral LLM internally
agents = create_agents()

# Assign tools to agents
agents['order'].tools = [order_lookup_tool]
agents['refund'].tools = [refund_processor_tool, order_lookup_tool]
agents['knowledge'].tools = [retrieve_knowledge, inventory_check_tool]

def route_to_agent(intent: Intent):
    """Route to appropriate agent based on intent"""
    routing = {
        Intent.ORDER_TRACKING: agents['order'],
        Intent.REFUND_REQUEST: agents['refund'],
        Intent.PRODUCT_INQUIRY: agents['knowledge'],
        Intent.TECHNICAL_SUPPORT: agents['knowledge'],
        Intent.GENERAL_INQUIRY: agents['knowledge']
    }
    return routing.get(intent, agents['knowledge'])

def handle_query(query: str, customer_id: str = "GUEST"):
    """Main function to handle customer queries"""
    print(f"\n{'='*80}")
    print(f"Customer Query: {query}")
    print(f"{'='*80}\n")

    # Classify intent
    intent, confidence = intent_classifier.classify_intent(query)
    print(f"Detected Intent: {intent.value} (confidence: {confidence:.2f})\n")

    # Route to agent
    selected_agent = route_to_agent(intent)
    print(f"Routing to: {selected_agent.role}\n")

    # Build context
    context = {"customer_id": customer_id, "intent": intent.value}

    # Create and execute task
    task = create_task(selected_agent, query, context)
    crew = Crew(
        agents=[selected_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()

    print(f"\n{'='*80}")
    print("Response:")
    print(f"{'='*80}")
    print(result)

    return result

if __name__ == "__main__":
    test_queries = [
        "Where is my order #12345?",
        "I need to return a damaged laptop",
        "What is your return policy?"
    ]
    print("\n" + "="*80)
    print("ShopEase Agentic RAG Customer Support System")
    print("="*80)
    for q in test_queries:
        handle_query(q)
        print("\n" * 2)
