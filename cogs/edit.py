from discord.ext import commands
from discord.ext.commands import Context

from core.checks import is_channel_owner


class Edit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["name"])
    @commands.guild_only()
    @is_channel_owner()
    async def rename(self, ctx: Context, *, name):
        """
        Rename your voice channel.
        ~
        {prefix}rename Sonus Appreciation Channel
        {prefix}rename cool
        """
        try:
            await ctx.author.voice.channel.edit(name=name)
        except Exception as e:
            return await ctx.send("An error occured: " + str(e))
        await ctx.send(f"Renamed channel to `{name}`.")


def setup(bot):
    bot.add_cog(Edit(bot))
