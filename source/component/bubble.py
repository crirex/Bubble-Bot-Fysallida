import random
from typing import Set, Union, List, Optional

from discord.ext import commands
from discord.ext.commands import Context, BadArgument
from discord.utils import find
import discord
from discord import Member, User

from globals import *
from btypes import *
from jsons import dump_json, trapped_users_json, Encoder
from formatter import formatter, import_pronouns
from .prefs import get_user_prefs


def get_filtered_possibility(blacklist: Set[Union[BubblePlay, BubbleType, BubbleColor, BubbleTag]],
                             play_type: BubblePlay = None,
                             bubble_type: BubbleType = None,
                             bubble_color: BubbleColor = None,
                             bubble_tags: Set[BubbleTag] = frozenset()
                             ) -> (str, bool, Optional[BubblePlay], Optional[BubbleType], Optional[BubbleColor]):
    if play_type in blacklist:
        return "Sorry, {they} {doesn't|v|don't} like to play like that.", False, None, None, None
    # noinspection PyTypeChecker
    play_types = set(BubblePlay).difference(blacklist) if play_type is None else {play_type}

    if bubble_type in blacklist:
        return "Sorry, {they} {doesn't|v|don't} like that kind of bubble.", False, None, None, None
    # noinspection PyTypeChecker
    bubble_types = set(BubbleType).difference(blacklist) if bubble_type is None else {bubble_type}

    if bubble_color in blacklist:
        return "Sorry, {they} {doesn't|v|don't} like that kind of bubble.", False, None, None, None
    # noinspection PyTypeChecker
    bubble_colors = set(BubbleColor).difference(blacklist) if bubble_color is None else {bubble_color}
    b_color = random.choice(list(bubble_colors))

    if blacklist.intersection([t.value for t in bubble_tags]):
        return "Sorry, {they} {doesn't|v|don't} like that kind of bubble.", False, None, None, None

    possibilities = list(
        filter(lambda text: text.play_type in play_types and text.bubble_type in bubble_types
               and text.tags >= bubble_tags
               and not text.tags.intersection(blacklist),

               trapping_text)
    )

    if not possibilities:
        return "It seems like I couldn't find anything to do.", False, None, None, None

    choice: TrappingText = random.choice(possibilities)
    return choice.text, True, choice.play_type, choice.bubble_type, b_color


def get_trapped_user(user_id: int) -> BubbleTrap:
    return find(lambda trap: trap.user == user_id, trapped_users)


def is_trapped(user_id: int) -> bool:
    return get_trapped_user(user_id) is not None


def get_all_members(ctx: Context) -> Union[List[Member], List[User]]:
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


def save_trapped_users():
    dump_json(trapped_users, trapped_users_json, cls=Encoder)


# noinspection PyPep8Naming
class me(commands.Converter):
    async def convert(self, ctx: Context, argument: str) -> Union[Member, User]:
        if argument.lower() == "me":
            return ctx.author
        else:
            raise BadArgument("\"{}\" could not be recognized as a valid self keyword.".format(argument))


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
                     user: Union[Member, User, me],
                     *tags: Union[BubblePlay, BubbleType, BubbleColor, BubbleTag, int],
                     ):
        author = ctx.author
        if user is None:
            all_users = get_all_members(ctx)
            if not all_users:
                await ctx.message.channel.send("No eligible member has been found.")
                return
            user = random.choice(all_users)
        bubble_type: BubbleType = find(lambda t: isinstance(t, BubbleType), tags)
        color_type: BubbleColor = find(lambda t: isinstance(t, BubbleColor), tags)
        play_type: BubblePlay = find(lambda t: isinstance(t, BubblePlay), tags)
        bubble_tags: Set[BubbleTag] = set(filter(lambda t: isinstance(t, BubbleTag), tags))
        seconds_trapped: int = find(lambda t: isinstance(t, int), tags)
        seconds_trapped = seconds_trapped if seconds_trapped is not None else maximum_bubble_time

        author_prefs = get_user_prefs(author.id)
        author_mention: str = author.mention if author_prefs.ping else author.display_name
        user_prefs = get_user_prefs(user.id)
        user_mention: str = user.mention if user_prefs.ping else user.display_name
        kwargs = {
            "user": user_mention,
            "author": author_mention
        }
        import_pronouns(kwargs, user_prefs.pronouns, author_prefs.pronouns)

        if is_trapped(user.id):
            await ctx.message.channel.send(formatter.vformat(
                "{user} is already trapped in a bubble and cannot be put in another one right now. "
                "You could get {them} out of the bubble if you want to.",
                [], kwargs))
            return

        seconds_trapped = maximum_bubble_time - seconds_trapped
        response, success, b_play, b_type, b_color = \
            get_filtered_possibility(user_prefs.blacklist, play_type, bubble_type, color_type, bubble_tags)
        channel = ctx.message.channel
        if success:
            trapped_users.append(BubbleTrap(**{
                "user": user.id,
                "bubble_play": b_play,
                "bubble_type": b_type,
                "bubble_color": b_color,
                "time": time.time() - seconds_trapped,
                "channel": channel.id,
                "tries": 0
            }))
            save_trapped_users()
            kwargs.update({
                "type": b_type.value,
                "color": b_color.value,
            })
        await ctx.message.channel.send(formatter.vformat(response, [], kwargs))

    # Free yourself or someone else someone from a bubble
    @commands.command(name='pop',
                      description="Let's someone free.",
                      brief="I get someone out of their bubble zone.",
                      aliases=['letGo', 'popBubble', 'lego', 'letgo', 'popbubble', 'release'],
                      pass_context=True)
    async def leave_bubble(self, ctx: Context, user: Union[Member, User, me, None]):
        author = ctx.author
        if user is None:
            user = ctx.message.author
        author_prefs = get_user_prefs(author.id)
        author_mention: str = author.mention if author_prefs.ping else author.display_name
        user_prefs = get_user_prefs(user.id)
        user_mention: str = user.mention if user_prefs.ping else user.display_name
        kwargs = {
            "user": user_mention,
            "author": author_mention
        }
        import_pronouns(kwargs, user_prefs.pronouns, author_prefs.pronouns)

        update = False

        if is_trapped(author.id):
            if author.id != user.id:
                await ctx.message.channel.send(formatter.vformat(
                    "{author} is inside a bubble and is unable to pop anyone else's bubble because of that. "
                    "{their!c} actions being limited to the confines of the bubble.",
                    [], kwargs))
            else:
                current_user = get_trapped_user(author.id)
                current_user.tries += 1
                kwargs.update({
                    "type": current_user.bubble_type.value,
                    "color": current_user.bubble_color.value,
                })
                if current_user.tries >= maximum_number_of_popping_times:
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
                    if current_user.tries >= maximum_number_of_popping_times - 1:
                        response += "The bubble seems to have lost some of its resistance after " \
                                    "so many attempts to free yourself."

                    await ctx.message.channel.send(formatter.vformat(response, [], kwargs))
                    update = True
        else:
            if is_trapped(user.id):
                current_user = get_trapped_user(user.id)
                kwargs.update({
                    "type": current_user.bubble_type.value,
                    "color": current_user.bubble_color.value,
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
            save_trapped_users()
