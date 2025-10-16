"""ShopEase Agentic RAG System"""

import os
from dotenv import load_dotenv
from crewai import Crew, Process
from langchain_openai import ChatOpenAI

from intent_classifier.model import IntentClassifier, Intent
from tools.shopease_tools import order_lookup_tool, refund_processor_tool, inventory_check_tool
from agents.crew_setup import create_agents, create_task
from integrations.pathway_rag import retrieve_knowledge

# Load environment
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize components
intent_classifier = IntentClassifier()
agents = create_agents(llm)

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
    
    # Step 1: Classify intent
    intent, confidence = intent_classifier.classify_intent(query)
    print(f"Detected Intent: {intent.value} (confidence: {confidence:.2f})")
    
    # Step 2: Route to agent
    selected_agent = route_to_agent(intent)
    print(f"Routing to: {selected_agent.role}\n")
    
    # Step 3: Create context
    context = {
        "customer_id": customer_id,
        "intent": intent.value
    }
    
    # Step 4: Execute task
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
    # Test queries
    test_queries = [
        "Where is my order #12345?",
        "I need to return a damaged laptop for order #12345",
        "What is your return policy?",
    ]
    
    print("\n" + "="*80)
    print("ShopEase Agentic RAG Customer Support System")
    print("="*80)
    
    for query in test_queries:
        try:
            handle_query(query)
        except Exception as e:
            print(f"Error: {e}")
        print("\n" * 2)
