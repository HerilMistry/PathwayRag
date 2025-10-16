from intent_classifier.model import IntentClassifier

classifier = IntentClassifier()

test_queries = [
    "Where is my order #12345?",
    "I want a refund",
    "Do you have this product in stock?",
    "This is unacceptable! I need a manager!"
]

print("Testing Intent Classification:\n")
for query in test_queries:
    intent, confidence = classifier.classify_intent(query)
    print(f"Query: {query}")
    print(f"Intent: {intent.value} (confidence: {confidence:.2f})\n")
