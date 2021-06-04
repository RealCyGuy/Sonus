import discord
from discord.ext import commands
from discord.ext.commands import Context

from core.checks import is_channel_owner


class Edit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["name"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    @is_channel_owner()
    @commands.guild_only()
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

    @commands.command(aliases=["lock"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    @is_channel_owner()
    @commands.guild_only()
    async def limit(self, ctx: Context, limit: int = 0):
        """
        Add a member limit to your voice channel.
        Leave limit blank to remove the current limit or make the limit equal to the number of users in the call.
        ~
        {prefix}limit
        {prefix}limit 5
        """
        if limit < 0:
            return await ctx.send("Limit cannot be negative.")
        elif limit > 100:
            return await ctx.send("Limit has to be under 100.")
        if limit == 0 and ctx.author.voice.channel.user_limit == 0:
            limit = len(ctx.author.voice.channel.members)
        try:
            await ctx.author.voice.channel.edit(user_limit=limit)
        except Exception as e:
            return await ctx.send("An error occured: " + str(e))
        await ctx.send(f"Changed limit to `{limit}`.")

    @commands.command(aliases=["rate"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    @is_channel_owner()
    @commands.guild_only()
    async def bitrate(self, ctx: Context, rate: int):
        """
        Change the channel's bitrate.
        ~
        {prefix}bitrate 32
        {prefix}bitrate 64
        """
        if rate < 8 or rate > 96:
            return await ctx.send("Limit has to be from 8-96kbps.")
        try:
            await ctx.author.voice.channel.edit(bitrate=rate * 1000)
        except Exception as e:
            return await ctx.send("An error occured: " + str(e))
        await ctx.send(f"Changed bitrate to `{rate}` kbps.")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @is_channel_owner()
    @commands.guild_only()
    async def ban(self, ctx: Context, *, user: discord.Member):
        """
        Remove's join permissions and kicks out a user.
        ~
        {prefix}ban @RealCyGuy#0001
        {prefix}ban 543225108135673877
        """
        name = user.name + "#" + user.discriminator
        try:
            await ctx.author.voice.channel.set_permissions(
                user, connect=False, reason=f"Banned from voice channel by {name}.",
            )
        except Exception as e:
            return await ctx.send("An error occured: " + str(e))
        try:
            await user.edit(
                voice_channel=None, reason="Kicked from voice channel by {name}."
            )
        except Exception as e:
            return await ctx.send("An error occured: " + str(e))
        await ctx.send(f"Banned {name}.")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @is_channel_owner()
    @commands.guild_only()
    async def unban(self, ctx: Context, *, user: discord.Member):
        """
        Unbans a user from joining the channel.
        ~
        {prefix}unban random guy
        {prefix}unban 543225108135673877
        """
        name = user.name + "#" + user.discriminator
        try:
            await ctx.author.voice.channel.set_permissions(
                user, connect=None, reason=f"Unbanned from voice channel by {name}.",
            )
        except Exception as e:
            return await ctx.send("An error occured: " + str(e))
        await ctx.send(f"Unbanned {name}.")


def setup(bot):
    bot.add_cog(Edit(bot))
