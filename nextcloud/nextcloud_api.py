from typing import Any
import aiohttp

class NextCloudAPI:
    BASE_URL = 'https://admin.gsus.work/{endpoint}'

    def __init__(self, secret: str):
        self.secret = secret

    def get_headers(self):
        return {
            #'Content-Type': 'application/json',
            'Authorization': 'Basic VGhlSW5hdG9ySW5hdG9yOnNkSlhDLWZubmdpLUZuVHdFLVlKdG01LXlySjNr',
        }

    async def get(self, endpoint, qps: dict[str, Any]) -> dict[str, Any]:
        url = self.BASE_URL.format(endpoint=endpoint.lstrip('/'))
        headers = self.get_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=qps) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def post(self, endpoint, data: dict[str, Any], headers: dict[str, str] = None):
        url = self.BASE_URL.format(endpoint=endpoint.lstrip('/'))
        headers = self.get_headers() | (headers or {})

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def create_new_account(self, user_id: int) -> dict[str, Any]:
        return await self.post(
            '/index.php/apps/app_api/proxy/flow/api/w/admins/jobs/run_wait_result/f/u/wapp_admin/discord_account_creation',
            data={'user_id': str(user_id)}
        )
