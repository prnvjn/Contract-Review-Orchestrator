import httpx
from typing import Dict, Any

class CRMClient:
    """
    Mocked client for FollowUpBoss to sync transaction milestones.
    """
    def __init__(self):
        self.webhook_url = "https://api.followupboss.com/v1/webhooks" # Placeholder

    async def sync_transaction_milestones(self, request_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates syncing data to a CRM via a webhook.
        """
        # In a real app, this would be an httpx.post call
        # print(f"DEBUG: Syncing to CRM for request {request_id}: {data}")
        
        return {
            "status": "success",
            "synced_at": "2023-06-13T12:00:00Z",
            "crm_id": f"fub_{request_id[:8]}",
            "message": "Milestones successfully synced to FollowUpBoss"
        }

crm_client = CRMClient()
