"""Tools for ShopEase Agents"""

from langchain.tools import tool
from datetime import datetime, timedelta
import random

# Mock Order Database
MOCK_ORDERS = {
    "12345": {
        "order_id": "12345",
        "customer_id": "C001",
        "items": ["Laptop", "Mouse"],
        "status": "shipped",
        "tracking_number": "TRK987654321",
        "estimated_delivery": "2025-10-20",
        "carrier": "FedEx"
    },
    "67890": {
        "order_id": "67890",
        "customer_id": "C002",
        "items": ["Phone Case"],
        "status": "processing",
        "tracking_number": None,
        "estimated_delivery": "2025-10-22",
        "carrier": None
    }
}

@tool
def order_lookup_tool(order_id: str) -> str:
    """Look up order status and tracking information"""
    order = MOCK_ORDERS.get(order_id)
    
    if not order:
        return f"Order #{order_id} not found. Please verify the order number."
    
    response = f"Order Status for #{order_id}:\n"
    response += f"- Items: {', '.join(order['items'])}\n"
    response += f"- Status: {order['status'].title()}\n"
    response += f"- Estimated Delivery: {order['estimated_delivery']}"
    
    if order.get('tracking_number'):
        response += f"\n- Tracking: {order['tracking_number']}"
        response += f"\n- Carrier: {order['carrier']}"
    
    return response

@tool
def refund_processor_tool(order_id: str, reason: str) -> str:
    """Initiate a refund for an order"""
    if order_id not in MOCK_ORDERS:
        return f"Cannot process refund: Order #{order_id} not found."
    
    refund_id = f"REF{random.randint(10000, 99999)}"
    processing_days = random.randint(5, 7)
    
    return f"""Refund Request Submitted Successfully!

- Order ID: #{order_id}
- Refund ID: {refund_id}
- Reason: {reason}
- Processing Time: {processing_days} business days
- Refund Method: Original payment method

You will receive a confirmation email shortly."""

@tool
def inventory_check_tool(product_name: str) -> str:
    """Check product availability"""
    in_stock = random.choice([True, False])
    quantity = random.randint(0, 50) if in_stock else 0
    
    if in_stock:
        return f"{product_name} is IN STOCK. Available quantity: {quantity} units."
    else:
        restock_date = (datetime.now() + timedelta(days=random.randint(5, 14))).strftime("%Y-%m-%d")
        return f"{product_name} is OUT OF STOCK. Expected restock date: {restock_date}"

# Export all tools
SHOPEASE_TOOLS = [
    order_lookup_tool,
    refund_processor_tool,
    inventory_check_tool
]
