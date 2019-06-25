from discord.ext import commands
from globals import *
import random
import time


class Bubbles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Puts someone in a bubble
    @commands.command(name='bubble',
                      description="Bubbles someone",
                      brief="I use bubbles to play with someone",
                      aliases=['putInABubble', 'putInBubble'],
                      pass_context=True)
    async def bubble(self, ctx, user=None, bubble_type='#', color_type='#',
                     seconds_trapped: int = maximum_bubble_time, play_type='#', ):
        if user is None:
            all_users = get_all_members(ctx)
            if not all_users:
                await ctx.message.channel.send("No eligible member has been found.")
                return
            user = (random.choice(all_users)).mention
        else:
            if trapped(user):
                await ctx.message.channel.send(
                    "{0} is already trapped in a bubble and cannot be put in another one right now. "
                    "You could get him out of the bubble if you want to."
                    .format(user))
                return
            if (user.lower() == "pop") | (user.lower() == "release"):
                user = bubble_type
                print(user)
                await ctx.message.channel.send(
                    "{0}, you need to use the \"+pop @name\" command"
                    .format(ctx.message.author.mention))
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
            "user_mention": user,
            "bubble_type": bubble_type,
            "bubble_color": color_type,
            "time": time.time() - seconds_trapped,
            "channel": user_channel.id,
            "tries": 0
        })
        dump_json(trapped_users, trapped_users_json)
        await ctx.message.channel.send(response.format(user, color_type))

    # Free yourself or someone else someone from a bubble
    @commands.command(name='pop',
                      description="Let's someone free.",
                      brief="I get someone out of their bubble zone.",
                      aliases=['letGo', 'popBubble', 'lego', 'letgo', 'popbubble', 'release'],
                      pass_context=True)
    async def leave_bubble(self, ctx, user=None):
        if user is None:
            user = ctx.message.author.mention

        if type(user) is str:
            for current_user in trapped_users:
                if ctx.message.author.mention == current_user:
                    await ctx.message.channel.send(
                        "{0} is inside a bubble and is unable to pop anyone else's bubble because of that, "
                        "{0}'s actions being limited to the insides of the bubble"
                        .format(user))
                    return

            for current_user in trapped_users:
                if user == current_user["user_mention"]:
                    if ctx.message.author.mention == user:
                        current_user["tries"] += 1
                        if current_user["tries"] >= maximum_number_of_popping_times:
                            text_to_say = [
                                "The {2} {1} bubble in which {0} was just pops after so many tries to escape "
                                "and {0} is now free. (Maybe there was some unknown force that let you free)",
                                "I reach out and touch {0}'s {2} {1} bubble in which "
                                "{0} was trapped in, after which it pops and {0} is now free."]

                            await ctx.message.channel.send(random.choice(text_to_say)
                                                           .format(current_user["user_mention"],
                                                                   current_user["bubble_type"],
                                                                   current_user["bubble_color"]))
                            trapped_users.remove(current_user)
                            dump_json(trapped_users, trapped_users_json)
                            return

                        text_to_say = "{0} tries to pop the bubble but only manages to stretch it, " \
                                      "seeing how resilient it is and unable to pop it. " \
                                      "Only someone else may pop it or it will pop by itself after some time. "
                        if current_user["tries"] >= maximum_number_of_popping_times - 1:
                            text_to_say += "The bubble seems to have lost some of it's resistance after " \
                                           "so many attempts to free yourself."

                        await ctx.message.channel.send(text_to_say.format(user))
                        dump_json(trapped_users, trapped_users_json)
                        return
                    else:
                        await ctx.message.channel.send(
                            "{3} pops the {2} {1} bubble in which {0} was just, freeing {0} "
                            "from the bubbly, comfy prison"
                            .format(
                                current_user["user_mention"],
                                current_user["bubble_type"],
                                current_user["bubble_color"],
                                ctx.message.author.mention))
                        trapped_users.remove(current_user)
                        dump_json(trapped_users, trapped_users_json)
                        return

            await ctx.message.channel.send("{0} isn't trapped in any kind of bubble. "
                                           "Maybe {0} needs to be in one :3".format(user))
        else:
            await ctx.message.channel.send("{0}, you need to specify who to let go.".format(ctx.message.author.mention))
