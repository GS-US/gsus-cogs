from io import BytesIO
from typing import Optional
from urllib.error import HTTPError

import discord
from redbot.core.utils.chat_formatting import inline

from nextcloud.nextcloud_api import NextCloudAPI
from tsutils.cogs.apicog import CogWithEndpoints, endpoint

from redbot.core import commands

class NextCloud(CogWithEndpoints):
    """A cog to interface with NextCloud."""

    GSUS_SERVER_ID = 1054471846436798535

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.api = None

    async def cog_load(self):
        await super().cog_load()

        keys = await self.bot.get_shared_api_tokens('nextcloud')
        if 'nextcloud_secret' not in keys:
            raise ValueError("NextCloud cog requires 'nextcloud_secret' shared_api_token. Set this via [p]set api")
        if 'windmill_secret' not in keys:
            raise ValueError("NextCloud cog requires 'windmill_secret' shared_api_token. Set this via [p]set api")
        self.api = NextCloudAPI(keys['nextcloud_secret'], keys['windmill_secret'])

    async def red_get_data_for_user(self, *, user_id):
        """Get a user's personal data."""
        data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """Delete a user's personal data.

        No personal data is stored in this cog.
        """
        return

    @endpoint("user_info")
    async def user_info(self, user_id: int):
        """Get info about a user."""
        try:
            member = await self.bot.get_guild(self.GSUS_SERVER_ID).fetch_member(user_id)
        except discord.NotFound:
            return {
                'response': {'error': 'Member not in GSUS server.'},
                'status': 404
            }

        return {
                'response': {
                    'avatar_url': member.avatar.url if member.avatar else None,
                    'name': member.name,
                    'account_creation': member.created_at.timestamp(),
                    'roles': [role.id for role in member.roles],
                },
                'status': 200
            }

    @commands.group()
    async def nextcloud(self, ctx):
        """Interface with NextCloud."""
        ...

    @nextcloud.group()
    async def account(self, ctx):
        """Deal with your account."""
        ...

    @account.command()
    async def new(self, ctx, user: Optional[discord.User]):
        """Create a new account."""
        user = user or ctx.author

        try:
            resp = await self.api.create_new_account(user.id)
        except HTTPError as e:
            if e.response.status_code == 409:
                await ctx.send("You already have an account.")
            raise

        print(resp)
        username = resp['username']
        password = resp['password']
        await ctx.tick()
        await user.send(
            f"Your account has been created.\n\n"
            f"Your username is {inline(username)} and your password is {inline(password)}.")



