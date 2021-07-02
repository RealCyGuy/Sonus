import asyncio
import inspect
import os
from datetime import datetime
from difflib import get_close_matches

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord_components import ButtonStyle, Button
from humanize import precisedelta

from bot import __version__


class SonusHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        bot = self.context.bot

        cogs = [bot.get_cog("Setup"), bot.get_cog("Edit"), bot.get_cog("Misc")]
        cog_commands = [cog.get_commands() for cog in cogs]

        help_embed = discord.Embed(
            description=f"You can get started by using `{self.clean_prefix}create`."
        )
        help_embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(
            text=f"Use {self.clean_prefix}help [command] to get help for a specific command."
        )

        for cog_command in cog_commands:
            value = "\n".join(
                [
                    f"**{self.clean_prefix}{command.qualified_name}** - *{command.short_doc.strip()}*"
                    for command in cog_command
                ]
            )
            value = value.replace(" - **", "")
            help_embed.add_field(
                name=cog_command[0].cog_name, value=value, inline=False
            )
        await self.get_destination().send(embed=help_embed)

    async def send_command_help(self, command):
        bot = self.context.bot

        help_embed = discord.Embed()
        help_embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(
            text=f"Use {self.clean_prefix}help [command] to get help for a specific command."
        )

        help_embed.title = (
            f"{self.clean_prefix}{command.qualified_name} {command.signature}"
        )
        description = command.help.split("~")
        help_embed.add_field(
            name="Description",
            value=description[0].replace("{prefix}", self.clean_prefix),
        )
        help_embed.add_field(
            name="Usage",
            value="```"
            + description[1].strip("\n ").replace("{prefix}", self.clean_prefix)
            + "```",
        )
        try:
            help_embed.add_field(
                name="Note",
                value=description[2].replace("{prefix}", self.clean_prefix),
                inline=False,
            )
        except IndexError:
            pass
        if command.aliases:
            aliases = "`" + "`, `".join(command.aliases) + "`"
        else:
            aliases = "No aliases."
        help_embed.add_field(name="Aliases", value=aliases, inline=False)
        help_embed.set_footer(
            text=f"Use {self.clean_prefix}help to see all the commands."
            + "\n"
            + "\u2501" * 40
            + "\n"
            + "[]'s are optional arguments. <>'s are required arguments."
        )
        await self.get_destination().send(embed=help_embed)

    async def send_error_message(self, error):
        command = self.context.kwargs.get("command")
        command_names = set()
        for cmd in self.context.bot.walk_commands():
            if not cmd.hidden:
                command_names.add(cmd.qualified_name)
                for alias in cmd.aliases:
                    command_names.add(alias)
        closest = get_close_matches(command, command_names, 2)
        if not closest:
            closest = get_close_matches(command, command_names, 1, 0)
        closest = "` or `".join(closest)
        embed = discord.Embed(
            description=f"Command `{command}` not found. Did you mean `{closest}`?"
        )
        embed.colour = 2228207
        await self.get_destination().send(embed=embed)


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = SonusHelpCommand(
            verify_checks=False,
            command_attrs={
                "help": """
                    Shows this help message.
                    ~
                    {prefix}help
                    {prefix}help create
                    """
            },
        )
        self.bot.help_command.cog = self

    @commands.command(aliases=["who", "what", "when", "where", "why"])
    @commands.cooldown(1, 4, commands.BucketType.member)
    async def about(self, ctx: Context):
        """
        Get info and links!
        ~
        {prefix}about
        """
        embed = discord.Embed(
            description="Sonus is a fast, simple, and open-source auto voice channel discord bot created by Cyrus Yip. "
            + "You can view all the commands with `@Sonus help`."
        )
        embed.colour = 2228207
        embed.add_field(name="Version", value="v" + __version__)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(
            name="Latency", value="{:.3f}ms".format(self.bot.latency * 1000)
        )
        embed.add_field(
            name="Uptime", value=precisedelta(datetime.now() - self.bot.startup)
        )
        await ctx.send(
            embed=embed,
            components=[
                [
                    Button(
                        style=ButtonStyle.URL,
                        label="Invite",
                        url="https://discord.com/oauth2/authorize?client_id="
                        + str(self.bot.user.id)
                        + "&permissions=285280272&scope=bot",
                    ),
                    Button(
                        style=ButtonStyle.URL,
                        label="GitHub",
                        url="https://github.com/realcyguy/sonus",
                    ),
                    Button(
                        style=ButtonStyle.URL,
                        label="Cyrus Yip",
                        url="https://realcyguy.netlify.app",
                    ),
                ]
            ],
        )

    @commands.command(aliases=["add", "inv", "coolbotcanihaveitinmyserver"])
    @commands.cooldown(1, 4, commands.BucketType.member)
    async def invite(self, ctx: Context):
        """
        Get the invite link of the bot.

        Why are you looking at the help for invite??
        ~
        {prefix}invite
        """
        await ctx.send(
            "Here's my invite link: https://discord.com/oauth2/authorize?client_id="
            + str(self.bot.user.id)
            + "&permissions=285288464&scope=bot"
        )

    @commands.command(aliases=["github", "gh"])
    @commands.cooldown(1, 4, commands.BucketType.member)
    async def source(self, ctx: Context, command=None):
        """
        Get the source code of a command.

        Use it by itself to get the GitHub link.
        ~
        {prefix}source
        {prefix}source rename
        """
        # await ctx.send(
        #     "You can find the source here: https://github.com/realcyguy/sonus"
        # )
        source_url = "https://github.com/RealCyGuy/Sonus"
        prefix = "@" + self.bot.user.name + " "
        if command is None:
            embed = discord.Embed(
                title="Sonus's Source Code",
                description=source_url
                + "\n\n"
                + "To get the source code for a specific command, use "
                f"`{prefix}{ctx.invoked_with} [command]`",
                colour=2228207,
            )
            await ctx.send(embed=embed)
            return

        obj = self.bot.get_command(command)
        if obj is None:
            return await ctx.send("Command not found!")

        src = obj.callback.__code__
        lines, file_start = inspect.getsourcelines(src)
        sourcecode = inspect.getsource(src).replace("```", "")
        if obj.callback.__module__.startswith("discord"):
            location = obj.callback.__module__.replace(".", "/") + ".py"
            source_url = "https://github.com/Rapptz/discord.py"
            branch = "master"
        else:
            location = os.path.relpath(src.co_filename).replace("\\", "/")
            branch = "main"

        embed = discord.Embed(
            title=f"Source code of {prefix}{command}.", colour=2228207
        )

        sourcecode = sourcecode.splitlines(True)
        for index, line in enumerate(sourcecode):
            if line.startswith(" " * 4):
                sourcecode[index] = line[4:]
        sourcecode = "".join(sourcecode)

        file_end = file_start + len(lines) - 1
        link = "{}/blob/{}/{}#L{}-L{} ".format(
            source_url, branch, location, file_start, file_end
        )
        pages = []
        msg = "```py\n"
        lines = sourcecode.splitlines(True)
        for index, line in enumerate(lines + [""]):
            if msg != "```py\n":
                if len(link) + len(line) + len(msg) + 3 > 2000 or index == len(lines):
                    msg += "```"
                    page = embed.copy()
                    page.description = link + msg
                    pages.append(page)
                    msg = "```py\n"
            msg += line
        message = await ctx.send(
            embed=pages[0].copy().set_footer(text="1/" + str(len(pages)) + " pages")
        )
        reactions = ["◀", "▶"]
        for re in reactions:
            await message.add_reaction(re)

        def check(r, u):
            return r.message.id == message.id and u == ctx.author

        page = 0
        while True:
            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
                if reaction.emoji in reactions:
                    reaction_index = -1
                    if reaction.emoji == reactions[0] and page > 0:
                        page -= 1
                        reaction_index = 0
                    if reaction.emoji == reactions[1] and page < len(pages) - 1:
                        page += 1
                        reaction_index = 1
                    if reaction_index >= 0:
                        await message.edit(
                            embed=pages[page]
                            .copy()
                            .set_footer(
                                text=str(page + 1) + "/" + str(len(pages)) + " pages"
                            )
                        )
                        try:
                            await message.remove_reaction(
                                reactions[reaction_index], ctx.author
                            )
                        except discord.Forbidden:
                            pass
            except asyncio.TimeoutError:
                for re in reactions:
                    await message.remove_reaction(re, self.bot.user)
                    try:
                        await message.remove_reaction(re, ctx.author)
                    except discord.Forbidden:
                        pass


def setup(bot):
    bot.add_cog(Misc(bot))
