"""Intent Classification for Customer Support"""

from typing import Dict, List, Tuple
from enum import Enum

class Intent(Enum):
    ORDER_TRACKING = "order_tracking"
    REFUND_REQUEST = "refund_request"
    PRODUCT_INQUIRY = "product_inquiry"
    TECHNICAL_SUPPORT = "technical_support"
    GENERAL_INQUIRY = "general_inquiry"
    URGENT_ESCALATION = "urgent_escalation"

class IntentClassifier:
    def __init__(self, llm_model=None):
        self.llm = llm_model
        self.intent_keywords = self._build_keyword_map()
    
    def _build_keyword_map(self) -> Dict[Intent, List[str]]:
        return {
            Intent.ORDER_TRACKING: [
                "track", "where is my order", "shipping", "delivery", 
                "order status", "when will", "tracking number"
            ],
            Intent.REFUND_REQUEST: [
                "refund", "return", "money back", "cancel order", 
                "damaged", "not as described", "defective"
            ],
            Intent.PRODUCT_INQUIRY: [
                "product", "item", "specifications", "features", 
                "available", "stock", "price", "cost"
            ],
            Intent.TECHNICAL_SUPPORT: [
                "not working", "broken", "error", "problem", 
                "issue", "help with", "how to use"
            ],
            Intent.URGENT_ESCALATION: [
                "angry", "furious", "unacceptable", "manager", 
                "complaint", "terrible", "worst"
            ]
        }
    
    def classify_intent(self, query: str) -> Tuple[Intent, float]:
        """Classify query intent with confidence score"""
        return self._keyword_classify(query)
    
    def _keyword_classify(self, query: str) -> Tuple[Intent, float]:
        query_lower = query.lower()
        scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[intent] = score / len(keywords)
        
        if not scores:
            return Intent.GENERAL_INQUIRY, 0.5
        
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] * 2, 1.0)
        
        return best_intent, confidence
