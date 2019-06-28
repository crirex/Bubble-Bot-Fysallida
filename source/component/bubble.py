import inspect

from discord.ext import commands
from discord.ext.commands import Context, BadUnionArgument
from discord.utils import find
import discord
from discord import Member, User
from globals import *
from jsons import dump_json, trapped_users_json
import random
import time
import typing
from formatter import formatter, import_pronouns
from .prefs import get_user_prefs


def get_trapped_user(user_id: int):
    return find(lambda user: user["user"] == user_id, trapped_users)


def is_trapped(user_id: int):
    return get_trapped_user(user_id) is not None


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
                     user: typing.Union[Member, User, str],
                     bubble_type='#',
                     color_type='#',
                     seconds_trapped: int = maximum_bubble_time,
                     play_type='#',
                     ):
        author = ctx.author
        if user is None:
            all_users = get_all_members(ctx)
            if not all_users:
                await ctx.message.channel.send("No eligible member has been found.")
                return
            user = random.choice(all_users)
        if isinstance(user, str):
            if user == "me":
                user = author
            else:
                raise BadUnionArgument(inspect.signature(Bubbles.bubble.callback).parameters["user"],
                                       (Member, User), [])

        author_prefs = get_user_prefs(author.id)
        author_mention: str = author.mention if author_prefs["ping"] else author.display_name
        user_prefs = get_user_prefs(user.id)
        user_mention: str = user.mention if user_prefs["ping"] else user.display_name
        kwargs = {
            "user": user_mention,
            "author": author_mention
        }
        import_pronouns(kwargs, user_prefs["pronouns"], author_prefs["pronouns"])

        if is_trapped(user.id):
            await ctx.message.channel.send(formatter.vformat(
                "{user} is already trapped in a bubble and cannot be put in another one right now. "
                "You could get {them} out of the bubble if you want to.",
                [], kwargs))
            return
        if (user_mention.lower() == "pop") or (user_mention.lower() == "release"):
            user_mention = bubble_type
            print(user_mention)
            await ctx.message.channel.send(formatter.vformat(
                "{author}, you need to use the \"+pop @name\" command",
                [], kwargs))
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
        channel = ctx.message.channel
        trapped_users.append({
            "user": user.id,
            "bubble_type": bubble_type,
            "bubble_color": color_type,
            "time": time.time() - seconds_trapped,
            "channel": channel.id,
            "tries": 0
        })
        dump_json(trapped_users, trapped_users_json)
        kwargs.update({
            "type": bubble_type,
            "color": color_type,
        })
        await ctx.message.channel.send(formatter.vformat(response, [], kwargs))

    # Free yourself or someone else someone from a bubble
    @commands.command(name='pop',
                      description="Let's someone free.",
                      brief="I get someone out of their bubble zone.",
                      aliases=['letGo', 'popBubble', 'lego', 'letgo', 'popbubble', 'release'],
                      pass_context=True)
    async def leave_bubble(self, ctx: Context, user: typing.Optional[typing.Union[Member, User, str]]):
        author = ctx.author
        if user is None:
            user = ctx.message.author
        if isinstance(user, str):
            if user == "me":
                user = author
            else:
                raise BadUnionArgument(inspect.signature(Bubbles.bubble.callback).parameters["user"],
                                       (Member, User), [])
        author_prefs = get_user_prefs(author.id)
        author_mention: str = author.mention if author_prefs["ping"] else author.display_name
        user_prefs = get_user_prefs(user.id)
        user_mention: str = user.mention if user_prefs["ping"] else user.display_name
        kwargs = {
            "user": user_mention,
            "author": author_mention
        }
        import_pronouns(kwargs, user_prefs["pronouns"], author_prefs["pronouns"])

        update = False

        if is_trapped(author.id):
            if author.id != user.id:
                await ctx.message.channel.send(formatter.vformat(
                    "{author} is inside a bubble and is unable to pop anyone else's bubble because of that. "
                    "{their!c} actions being limited to the confines of the bubble.",
                    [], kwargs))
            else:
                current_user = get_trapped_user(author.id)
                current_user["tries"] += 1
                kwargs.update({
                    "type": current_user["bubble_type"],
                    "color": current_user["bubble_color"],
                })
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
            if is_trapped(user.id):
                current_user = get_trapped_user(user.id)
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
