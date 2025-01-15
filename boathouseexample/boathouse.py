import httpx
import logging
from pydantic import BaseModel
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BoathouseResponse(BaseModel):
    paddleCustomerId: str
    billingPortalUrl: str
    pricingTableHtml: str
    activeSubscriptions: List[str]

class BoathouseApi:
    def __init__(self, config: dict):
        self.boathouse_api = config["BOATHOUSE_API"]
        self.boathouse_portal_id = config["BOATHOUSE_PORTAL_ID"]
        self.boathouse_secret = config["BOATHOUSE_SECRET"]
        logger.debug("BoathouseApi initialized with API URL: %s, Portal ID: %s", self.boathouse_api, self.boathouse_portal_id)

    async def get_boathouse_response(self, email: str, customer_id: str, return_url: Optional[str] = None) -> Optional[BoathouseResponse]:
        payload = {
            "portalId": self.boathouse_portal_id,
            "secret": self.boathouse_secret,
            "email": email,
            "paddleCustomerId": customer_id, 
            "returnUrl": return_url
        }

        logger.debug("Sending request to Boathouse API with payload: %s", payload)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.boathouse_api, json=payload)
                response.raise_for_status()
                logger.info("Received response from Boathouse API: %s", response.text)
            except httpx.HTTPStatusError as e:
                logger.error("HTTP error occurred: %s", e)
                raise
            except Exception as e:
                logger.error("An unexpected error occurred: %s", e)
                raise

        response_data = response.json()
        logger.debug("Parsed response data: %s", response_data)

        return BoathouseResponse(**response_data)

# Example usage
# async def main():
#     config = {
#         "BOATHOUSE_API": "https://example.com/api",
#         "BOATHOUSE_PORTAL_ID": "example_portal_id",
#         "BOATHOUSE_SECRET": "example_secret"
#     }
#     api = BoathouseApi(config)
#     response = await api.get_boathouse_response("email@example.com", "customer123")
#     print(response)

# To run the example, you'll need an asynchronous runtime, like asyncio.
