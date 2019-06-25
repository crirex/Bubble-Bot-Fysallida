from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Joins the voice channels of the person that used the command
    @commands.command(name='join',
                      pass_context=True)
    async def join_voice(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        print("Joined voice channel")

    # Leaves the voice channel
    @commands.command(name='leave',
                      pass_context=True)
    async def leave_voice(self, ctx):
        server = ctx.message.guild
        await server.voice_client.disconnect()
        print("Left voice channel")
