from difflib import get_close_matches

import discord
from discord.ext import commands
from discord.ext.commands import Context


class SonusHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        bot = self.context.bot

        cogs = [bot.get_cog("Setup"), bot.get_cog("Misc")]
        cog_commands = [cog.get_commands() for cog in cogs]

        help_embed = discord.Embed(
            description=f"Sonus is a fast, simple, and [open-source](https://github.com/realcyguy/Sonus \"GitHub\") "
                        f"auto voice channel discord bot created by [Cyrus Yip](https://realcyguy.netlify.app "
                        f"\"realcyguy.netlify.app\").\nYou can get started by using `{self.clean_prefix}create`.")
        help_embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(text=f"Use {self.clean_prefix}help [command] to get help for a specific command.")

        for cog_command in cog_commands:
            value = '\n'.join(
                [f"**{self.clean_prefix}{command.qualified_name}** - *{command.short_doc.strip()}*" for command in
                 cog_command])
            value = value.replace(" - **", "")
            help_embed.add_field(
                name=cog_command[0].cog_name,
                value=value
            )
        await self.get_destination().send(embed=help_embed)

    async def send_command_help(self, command):
        bot = self.context.bot

        help_embed = discord.Embed()
        help_embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(text=f"Use {self.clean_prefix}help [command] to get help for a specific command.")

        help_embed.title = f"{self.clean_prefix}{command.qualified_name} {command.signature}"
        description = command.help.split("~")
        help_embed.add_field(name="Description", value=description[0].replace("{prefix}", self.clean_prefix))
        help_embed.add_field(name="Usage",
                             value="```" + description[1].strip("\n ").replace("{prefix}", self.clean_prefix) + "```")
        try:
            help_embed.add_field(name="Note", value=description[2].replace("{prefix}", self.clean_prefix),
                                 inline=False)
        except IndexError:
            pass
        if command.aliases:
            aliases = "`" + "`, `".join(command.aliases) + "`"
        else:
            aliases = "No aliases."
        help_embed.add_field(name="Aliases", value=aliases, inline=False)
        help_embed.set_footer(
            text=f"Use {self.clean_prefix}help to see all the commands." +
                 "\n" + "\u2501" * 40 + "\n" +
                 "[]'s are optional arguments. <>'s are required arguments.")
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
        embed = discord.Embed(description=f"Command `{command}` not found. Did you mean `{closest}`?")
        embed.colour = 2228207
        await self.get_destination().send(embed=embed)


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = SonusHelpCommand(
            verify_checks=False,
            command_attrs={
                "help":
                    """
                    Shows this help message.
                    ~
                    {prefix}help
                    {prefix}help create
                    """
            },
        )
        self.bot.help_command.cog = self

    @commands.command(aliases=["add", "inv", "coolbotcanihaveitinmyserver"])
    async def invite(self, ctx: Context):
        """
        Get the invite link of the bot.
        ~
        {prefix}invite
        """
        await ctx.send(
            "Here's my invite link: https://discord.com/oauth2/authorize?client_id=" + str(
                self.bot.user.id) + "&permissions=16844816&scope=bot")

    @commands.command(aliases=["source"])
    async def github(self, ctx: Context):
        """
        Get the link to the GitHub repository.
        ~
        {prefix}github
        """
        await ctx.send("You can find the source here: https://github.com/realcyguy/sonus")


def setup(bot):
    bot.add_cog(Misc(bot))
