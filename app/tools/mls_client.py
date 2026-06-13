import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class MLSClient:
    """
    Client for SimplyRETS API to verify property data.
    Uses demo credentials by default.
    """
    def __init__(self):
        self.base_url = "https://api.simplyrets.com/properties"
        self.auth = (settings.SIMPLYRETS_KEY, settings.SIMPLYRETS_SECRET)
        
    async def verify_parcel_data(self, address: str) -> Dict[str, Any]:
        """
        Calls SimplyRETS API to verify property details.
        """
        try:
            async with httpx.AsyncClient() as client:
                # SimplyRETS supports a search query via 'q'
                response = await client.get(
                    self.base_url,
                    auth=self.auth,
                    params={"q": address, "limit": 1}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        listing = data[0]
                        return {
                            "status": "verified",
                            "mls_id": listing.get("listingId"),
                            "price_listed": listing.get("listPrice"),
                            "address": listing.get("address", {}).get("full"),
                            "source": "SimplyRETS Live API"
                        }
                
                return {
                    "status": "not_found",
                    "message": f"No active listing found for address: {address}",
                    "source": "SimplyRETS Live API"
                }
        except Exception as e:
            print(f"MLS API Error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "source": "SimplyRETS Live API"
            }

mls_client = MLSClient()
