# agents/crew_setup.py
"""CrewAI Multi-Agent Setup using Mistral as LLM backend"""

from crewai import Agent, Task, Crew, Process
from integrations.mistral_client import MistralClient

def create_agents():
    """Create all specialized agents using MistralClient"""
    # Instantiate single Mistral client for all agents
    mistral = MistralClient(
        endpoint="http://localhost:8000/v1/models/mistral-7b/infer"
    )
    
    # Triage Agent
    triage_agent = Agent(
        role="Customer Support Triage Specialist",
        goal="Classify customer queries and route to the right agent",
        backstory=(
            "You are an experienced triage specialist at ShopEase. "
            "You analyze queries and determine the best agent to handle them."
        ),
        verbose=True,
        allow_delegation=True,
        llm=mistral
    )
    
    # Order Tracking Agent
    order_agent = Agent(
        role="Order Tracking Specialist",
        goal="Help customers track their orders and provide shipping updates",
        backstory=(
            "You are a logistics expert who helps customers track orders "
            "and provide shipping updates."
        ),
        verbose=True,
        allow_delegation=False,
        llm=mistral,
        tools=[]  # Assign order lookup and history tools in main script
    )
    
    # Refund Processing Agent
    refund_agent = Agent(
        role="Refund Processing Specialist",
        goal="Process refund requests efficiently while ensuring policy compliance",
        backstory=(
            "You handle returns and refunds with empathy. "
            "You verify eligibility and process refunds."
        ),
        verbose=True,
        allow_delegation=False,
        llm=mistral,
        tools=[]  # Assign refund and order lookup tools in main script
    )
    
    # Knowledge Retrieval Agent
    knowledge_agent = Agent(
        role="Product Knowledge Expert",
        goal="Provide accurate information from the ShopEase knowledge base",
        backstory=(
            "You are the expert with deep knowledge of products, policies, and FAQs."
        ),
        verbose=True,
        allow_delegation=False,
        llm=mistral,
        tools=[]  # Assign RAG retrieval and inventory check tools in main script
    )
    
    return {
        'triage': triage_agent,
        'order': order_agent,
        'refund': refund_agent,
        'knowledge': knowledge_agent
    }


def create_task(agent: Agent, query: str, context: dict):
    """Create a task for an agent"""
    return Task(
        description=(
            f"Handle this customer query professionally:\n\n"
            f"Query: \"{query}\"\n"
            f"Context: {context}\n\n"
            "Provide a helpful, accurate response. Use your tools if needed."
        ),
        agent=agent,
        expected_output="Complete customer response with solution"
    )
