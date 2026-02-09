from io import BytesIO

import aiohttp
import discord

from tsutils.cogs.apicog import CogWithEndpoints, endpoint

from redbot.core import commands, Config, checks


class StrikeCardV2(CogWithEndpoints):
    """A cog to interface with the new strike card."""

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.config = Config.get_conf(self, identifier=3260)
        self.config.register_guild(
            identifier=None,
            notification_channel=None,
            message="A member just signed the strike card!")

        self.secret = None

    async def cog_load(self):
        await super().cog_load()

        keys = await self.bot.get_shared_api_tokens('strikecardv2')
        if 'secret' not in keys:
            raise ValueError("Strike card cog requires 'secret' shared_api_token. Set this via [p]set api")
        self.secret = keys['secret']

    async def red_get_data_for_user(self, *, user_id):
        """Get a user's personal data."""
        data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """Delete a user's personal data.

        No personal data is stored in this cog.
        """
        return

    @commands.group()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def strikecard(self, ctx):
        """Interface with the new strike card."""
        ...

    @strikecard.group()
    async def setup(self, ctx):
        """General cog setup."""
        ...

    @setup.command(ignore_extra=False)
    async def setidentifier(self, ctx, identifier: str):
        """Set the unique identifier for your region."""
        if await self.config.guild(ctx.guild).identifier() == identifier:
            await ctx.tick()
            return

        for _, data in (await self.config.all_guilds()).items():
            if data['identifier'] == identifier:
                await ctx.send("This identifier is already in use by another server.")
                return
        await self.config.guild(ctx.guild).identifier.set(identifier)
        await ctx.tick()

    @strikecard.group()
    async def notifications(self, ctx):
        """Setup notifications."""
        ...

    @notifications.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel to send notifications to."""
        await self.config.guild(ctx.guild).notification_channel.set(channel.id)
        await ctx.tick()

    @notifications.command()
    async def setmessage(self, ctx, *, message: str):
        """Set the message to send when a card is signed in your region."""
        await self.config.guild(ctx.guild).message.set(message)
        await ctx.tick()

    @endpoint("strikecardv2/new-signer")
    async def new_signer(self, request: aiohttp.web.Request):
        """Handle a new signee."""
        if request.headers.get('X-API-Key') != self.secret:
            return {'response': {'error': "Bad X-API-Key header."}, 'status': 401}

        # TODO: Add POST functionality
        identifier = request.query.get('chapter')
        print(identifier)
        for gid, data in (await self.config.all_guilds()).items():
            if data['identifier'] == identifier:
                guild = self.bot.get_guild(gid)
                break
        else:
            return {'response': {'error': "Identifier not found."}, 'status': 404}

        if guild is None:
            return {'response': {'error': "Guild with identifier is no longer accessible."}, 'status': 410}

        message = await self.config.guild(guild).message()
        cid = await self.config.guild(guild).notification_channel()

        if cid is None:
            return {'response': {'error': "Target guild has not set notification channel."}, 'status': 404}

        if (channel := guild.get_channel(cid)) is None:
            return {'response': {'error': "Announcement channel is no longer accessible."}, 'status': 410}

        try:
            await channel.send(message)
        except discord.Forbidden:
            return {'response': {'error': "No access in announcement channel."}, 'status': 401}

        return {'response': "Success", 'status': 200}



