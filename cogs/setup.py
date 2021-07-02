from discord.ext import commands
from discord.ext.commands import Context


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["start"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def create(self, ctx: Context):
        """
        Create an auto voice channel.

        hello :)
        ~
        {prefix}create
        """
        server = await self.bot.get_server(ctx.guild.id)
        channel = await ctx.guild.create_voice_channel("start vc!")
        server["autochannels"][str(channel.id)] = None
        await self.bot.servers.find_one_and_update(
            {"_id": str(ctx.guild.id)},
            {"$set": {"autochannels": server["autochannels"]}},
            upsert=True,
        )
        await ctx.send(
            f"Created voice channel with an id of `{channel.id}`. You can rename and move it and I'll automatically create voice channels!"
        )

    @commands.command(aliases=["tp"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def toggleposition(self, ctx: Context):
        """
        Change the position of created channels.

        You have to be in a channel created by the auto voice channel you want to change. This will not move current channels, move it yourself so lazy man.
        ~
        {prefix}toggleposition
        """
        if not ctx.author.voice:
            return await ctx.send(
                "You have to be in a voice channel to use this command."
            )
        server = await self.bot.get_server(ctx.guild.id)
        try:
            channel = server["channels"][str(ctx.author.voice.channel.id)]
        except KeyError:
            return await ctx.send(
                "You have to be in a voice channel created by me to use this command."
            )
        autochannel = server["autochannels"][str(channel["autochannel"])]
        position_bottom = True
        if autochannel:
            position_bottom = autochannel.get("positionbottom", True)
        else:
            server["autochannels"][str(channel["autochannel"])] = {}
        server["autochannels"][str(channel["autochannel"])][
            "positionbottom"
        ] = not position_bottom

        await self.bot.servers.find_one_and_update(
            {"_id": str(ctx.guild.id)},
            {"$set": {"autochannels": server["autochannels"]}},
            upsert=True,
        )

        await ctx.send(
            f"Set <#{channel['autochannel']}>'s future channels to spawn on the {'bottom' if position_bottom else 'top'}."
        )


def setup(bot):
    bot.add_cog(Setup(bot))
