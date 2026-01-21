from typing import Any
import aiohttp

class NextCloudAPI:
    BASE_URL = 'https://admin.gsus.work/{endpoint}'

    def __init__(self, nextcloud_secret: str, windmill_secret: str):
        self.nextcloud_secret = nextcloud_secret
        self.windmill_secret = windmill_secret

    def get_headers(self):
        return {
            # In theory we should have this, but for some reason it blows evrything up. Works without it so I guess we just don't use it :shrug: 
            # 'Content-Type': 'application/json',
            'Authorization': f'Basic {self.nextcloud_secret}',
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
            f'/index.php/apps/app_api/proxy/flow/api/w/admins/jobs/run_wait_result/f/u/wapp_admin/discord_account_creation?token={self.windmill_secret}',
            data={'user_id': str(user_id)}
        )
