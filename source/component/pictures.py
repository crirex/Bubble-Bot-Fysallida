import random
from typing import List, Dict, Optional

from datetime import datetime
from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context
import deviantart
from deviantart.deviation import Deviation

from jsons import config

albums = {
    "crirex": "61B9EF5B-7B0A-D912-E95F-17786A611E14",
    "autumn": "B2D7ED7B-8151-6354-CBB1-81CDD474CFB5"
}


def deviation_to_embed(deviation: Deviation) -> Embed:
    embed = Embed()
    embed.title = deviation.title
    embed.url = deviation.url
    embed.colour = Color.from_rgb(15, 204, 71)
    embed.set_thumbnail(url="https://st.deviantart.net/minish/main/logo/card_black_large.png")
    embed.set_author(name=deviation.author.username,
                     url="http://{}.deviantart.com".format(deviation.author.username),
                     icon_url=deviation.author.usericon)
    embed.set_image(url=deviation.content["src"])
    embed.timestamp = datetime.utcfromtimestamp(int(deviation.published_time))
    return embed


class Pictures(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.da = deviantart.Api(config.da_client_id, config.da_client_secret)
        self.collections: Dict[str, List[Deviation]] = {}

    def _collection(self, folder_id: str, username: str = "") -> List[Deviation]:
        results = []
        has_more = True
        next_offset = 0
        while has_more:
            response = self.da.get_collection(folder_id, username=username, offset=next_offset, limit=24)
            results.extend(response["results"])
            has_more = response["has_more"]
            next_offset = response["next_offset"]
        return results

    def _load_albums(self):
        for key in albums:
            self.collections[key] = self._collection(albums[key], username=config.da_username)

    async def load_albums(self):
        self._load_albums()

    @commands.command(name='albums',
                      pass_context=True)
    @commands.is_owner()
    async def albums(self, ctx: Context):
        async with ctx.channel.typing():
            await self.load_albums()
        await ctx.send("Albums updated.")

    @commands.command(name='pic',
                      pass_context=True)
    async def send_picture(self, ctx: Context, key: Optional[str]):
        if not self.collections:
            await ctx.send("No pictures available.")
            return
        if key is None:
            key = random.choice(list(albums.keys()))
        pic = random.choice(self.collections[key])
        await ctx.send(embed=deviation_to_embed(pic))
