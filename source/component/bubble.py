from discord.ext import commands
from discord.ext.commands import Context
import discord
from globals import *
import random
import time
import typing
from formatter import formatter
from .prefs import get_user_prefs


def is_trapped(user: str):
    return any([user == current_user["user_mention"] for current_user in trapped_users])


def get_trapped_user(user: str):
    return next((u for u in trapped_users if u["user_mention"] == user), None)


def get_all_members(ctx: Context):
    if isinstance(ctx.channel, discord.DMChannel):
        return [ctx.author]
    members = ctx.channel.recipients if isinstance(ctx.channel, discord.GroupChannel) else ctx.channel.members
    return list(filter(lambda member:
                       all([
                           not member.bot,
                           member.status == discord.Status.online or member.status == discord.Status.idle,
                           not is_trapped(member.mention)
                       ]),
                       members))


class Bubbles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Puts someone in a bubble
    @commands.command(name='bubble',
                      description="Bubbles someone",
                      brief="I use bubbles to play with someone",
                      aliases=['putInABubble', 'putInBubble'],
                      pass_context=True)
    async def bubble(self, ctx: Context,
                     user: typing.Optional[typing.Union[discord.Member, discord.User, str]],
                     bubble_type='#',
                     color_type='#',
                     seconds_trapped: int = maximum_bubble_time,
                     play_type='#',
                     ):
        if user is None:
            all_users = get_all_members(ctx)
            if not all_users:
                await ctx.message.channel.send("No eligible member has been found.")
                return
            user = random.choice(all_users)
        # Convert user to string
        user_mention: str = user.mention if isinstance(user, (discord.Member, discord.User)) else user
        author_prefs = get_user_prefs(ctx.author.id)
        user_prefs = get_user_prefs(user.id if isinstance(user, (discord.Member, discord.User)) else user)
        if is_trapped(user_mention):
            kwargs = {
                "user": user_mention,
            }
            kwargs.update(user_prefs["pronouns"])
            await ctx.message.channel.send(formatter.vformat(
                "{user} is already trapped in a bubble and cannot be put in another one right now. "
                "You could get {them} out of the bubble if you want to.",
                [], kwargs))
            return
        if (user_mention.lower() == "pop") or (user_mention.lower() == "release"):
            user_mention = bubble_type
            print(user_mention)
            await ctx.message.channel.send(
                "{author}, you need to use the \"+pop @name\" command"
                .format(author=ctx.message.author.mention))
            return

        if color_type == '#':
            color_type = get_random_color()

        if bubble_type == '#':
            bubble_type = get_random_bubble_type()

        color_type = color_type.lower()
        play_type = play_type.lower()
        bubble_type = bubble_type.lower()

        seconds_trapped = maximum_bubble_time - seconds_trapped
        response: str = get_filtered_possibility(play_type, bubble_type)
        user_channel = ctx.message.channel
        trapped_users.append({
            "user_mention": user_mention,
            "bubble_type": bubble_type,
            "bubble_color": color_type,
            "time": time.time() - seconds_trapped,
            "channel": user_channel.id,
            "tries": 0
        })
        dump_json(trapped_users, trapped_users_json)
        kwargs = {
            "user": user_mention,
            "color": color_type,
        }
        kwargs.update(user_prefs["pronouns"])
        await ctx.message.channel.send(formatter.vformat(response, [], kwargs))

    # Free yourself or someone else someone from a bubble
    @commands.command(name='pop',
                      description="Let's someone free.",
                      brief="I get someone out of their bubble zone.",
                      aliases=['letGo', 'popBubble', 'lego', 'letgo', 'popbubble', 'release'],
                      pass_context=True)
    async def leave_bubble(self, ctx: Context,
                           user: typing.Optional[typing.Union[discord.Member, discord.User, str]]
                           ):
        if user is None:
            user = ctx.message.author
        user_mention: str = user.mention if isinstance(user, (discord.Member, discord.User)) else user
        author_prefs = get_user_prefs(ctx.author.id)
        user_prefs = get_user_prefs(user.id if isinstance(user, (discord.Member, discord.User)) else user)

        update = False

        if is_trapped(ctx.author.mention):
            if ctx.author.mention != user_mention:
                kwargs = {
                    "author": ctx.author.mention
                }
                kwargs.update(author_prefs["pronouns"])
                await ctx.message.channel.send(formatter.vformat(
                    "{author} is inside a bubble and is unable to pop anyone else's bubble because of that. "
                    "{their!c} actions being limited to the confines of the bubble.",
                    [], kwargs))
            else:
                current_user = get_trapped_user(ctx.author.mention)
                current_user["tries"] += 1
                kwargs = {
                    "user": current_user["user_mention"],
                    "type": current_user["bubble_type"],
                    "color": current_user["bubble_color"],
                }
                kwargs.update(user_prefs["pronouns"])
                if current_user["tries"] >= maximum_number_of_popping_times:
                    responses = [
                        "The {color} {type} bubble in which {user} was in just pops after so many tries to escape "
                        "and {they} {'is|v|are'} now free. "
                        "(Maybe there was some unknown force that let {them} free)",
                        "I reach out and touch {user}'s {color} {type} bubble in which "
                        "{they} {'was|v|were'} trapped in, after which it pops and {they} {'is|v|are'} now free."]

                    await ctx.message.channel.send(formatter.vformat(random.choice(responses), [], kwargs))
                    trapped_users.remove(current_user)
                    update = True
                else:
                    response = "{user!c} tries to pop the bubble but only manages to stretch it, " \
                                  "seeing how resilient it is and unable to pop it. " \
                                  "Only someone else may pop it or it will pop by itself after some time. "
                    if current_user["tries"] >= maximum_number_of_popping_times - 1:
                        response += "The bubble seems to have lost some of its resistance after " \
                                       "so many attempts to free yourself."

                    await ctx.message.channel.send(formatter.vformat(response, [], kwargs))
                    update = True
        else:
            kwargs = {
                "user": user_mention,
                "author": ctx.message.author.mention,
            }
            kwargs.update(user_prefs["pronouns"])
            if is_trapped(user_mention):
                current_user = get_trapped_user(user_mention)
                kwargs.update({
                    "type": current_user["bubble_type"],
                    "color": current_user["bubble_color"],
                })
                await ctx.message.channel.send(formatter.vformat(
                    "{author!c} pops the {color} {type} bubble in which {user} was just in, freeing {them} "
                    "from the bubbly, comfy prison",
                    [], kwargs))
                trapped_users.remove(current_user)
                update = True
            else:
                await ctx.message.channel.send(formatter.vformat(
                    "{user!c} isn't trapped in any kind of bubble. "
                    "Maybe {they} {'needs|v|need'} to be in one :3",
                    [], kwargs))

        if update:
            dump_json(trapped_users, trapped_users_json)
