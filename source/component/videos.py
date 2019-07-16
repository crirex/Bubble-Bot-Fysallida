import random
from typing import List

from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context
from apiclient import discovery

from jsons import config


class Videos(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.service = discovery.build('youtube', 'v3', developerKey=config.yt_key)
        self.request = self.service.playlistItems().list(part="contentDetails",
                                                         playlistId="PL6ixvTgP-Rsy0Wjhz21-qJ4n42M1h4ZWZ")
        self.playlist: List[str] = []
        self._load_playlist()

    def _load_playlist(self):
        response = self.request.execute()
        self.playlist = ["https://youtu.be/" +
                         item["contentDetails"]["videoId"] for item in response["items"]]

    async def load_playlist(self):
        self._load_playlist()

    @commands.command(name='playlist',
                      pass_context=True)
    @commands.is_owner()
    async def playlist(self, ctx: Context):
        await self.load_playlist()
        await ctx.send("Playlist updated.")

    @commands.command(name='video',
                      pass_context=True)
    async def send_video(self, ctx):
        return await ctx.send(random.choice(self.playlist))
