from discord.ext import commands


def is_channel_owner():
    async def predicate(ctx):
        if ctx.author.voice:
            server = await ctx.bot.get_server(ctx.guild.id)
            channel = server["channels"].get(str(ctx.author.voice.channel.id), None)
            if channel:
                creator = channel.get("creator", None)
                if creator == ctx.author.id:
                    return True

        return False

    predicate.fail_msg = (
        "You have to be in a voice channel that you created with Sonus."
    )

    return commands.check(predicate)
