from io import BytesIO

from tsutils.cogs.apicog import CogWithEndpoints, endpoint

class NextCloud(CogWithEndpoints):
    """A cog to interface with NextCloud."""
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def red_get_data_for_user(self, *, user_id):
        """Get a user's personal data."""
        data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """Delete a user's personal data.

        No personal data is stored in this cog.
        """
        return

    @endpoint("hello")
    async def hello_world(self, name):
        """Adds two numbers."""
        return f"Hello, {name}!"


