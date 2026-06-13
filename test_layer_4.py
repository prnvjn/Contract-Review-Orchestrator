from app.guardrails.pre_flight import validate_document
from app.guardrails.mid_flight import check_financial_threshold
from app.guardrails.post_flight import scrub_legal_advice

def test_layer_4():
    print("🚀 Starting Layer 4: Guardrails Test...")

    # 1. Pre-flight test
    print("📋 Testing Pre-flight (Validation)...")
    valid_doc = "This is a Purchase Agreement for a buyer and seller."
    invalid_doc = "Hello world, this is a random text."
    
    assert validate_document(valid_doc)["is_valid"] == True
    assert validate_document(invalid_doc)["is_valid"] == False
    print("✅ Pre-flight passed.")

    # 2. Mid-flight test
    print("📋 Testing Mid-flight (Financial Circuit Breaker)...")
    assert check_financial_threshold(450000)["action"] == "PROCEED"
    assert check_financial_threshold(6000000)["action"] == "BLOCK"
    print("✅ Mid-flight passed.")

    # 3. Post-flight test
    print("📋 Testing Post-flight (Legal Advice Scrubber)...")
    safe_text = "The closing date is December 31st."
    unsafe_text = "I recommend you should consult an attorney to strike this clause."
    
    assert scrub_legal_advice(safe_text)["is_safe"] == True
    assert scrub_legal_advice(unsafe_text)["is_safe"] == False
    print("✅ Post-flight passed.")

    print("\n🏆 Layer 4 Guardrails Test: PASSED")

if __name__ == "__main__":
    test_layer_4()
