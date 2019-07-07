from discord.ext import tasks, commands
from discord.ext.commands import Bot


class Background(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.list_servers.start()

    def cog_unload(self):
        self.list_servers.cancel()

    # List all the servers from time to time so we could know where the bot is located
    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=3600)
    async def list_servers(self):
        print("Current servers:")
        for server in self.bot.guilds:
            print(server.name)

    @list_servers.before_loop
    async def list_server_before(self):
        await self.bot.wait_until_ready()
