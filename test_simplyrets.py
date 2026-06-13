import asyncio
from app.tools.mls_client import mls_client

async def test_live_mls():
    print("🚀 Testing SimplyRETS Demo API Integration...")
    
    # Using a common address that might be in demo data or just any string
    address = "123 Main St"
    result = await mls_client.verify_parcel_data(address)
    
    print(f"📊 Result: {result}")
    
    if result["status"] in ["verified", "not_found"]:
        print("🏆 SimplyRETS Demo Integration: SUCCESS")
    else:
        print(f"❌ Integration Failed: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_live_mls())
