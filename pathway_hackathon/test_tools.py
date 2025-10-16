from tools.shopease_tools import order_lookup_tool, refund_processor_tool

print("Testing Order Lookup Tool:")
result1 = order_lookup_tool.invoke({"order_id": "12345"})
print(result1)

print("\n" + "="*80 + "\n")

print("Testing Refund Processor Tool:")
result2 = refund_processor_tool.invoke({"order_id": "12345", "reason": "Damaged item"})
print(result2)
