__version__ = "1.1.1"

import os
import string

import discord
from discord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()


class Sonus(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, *args, **kwargs)
        # self.remove_command("help")
        self.loading_cogs = ["cogs.setup", "cogs.edit", "cogs.misc"]
        # Init mongodb
        self.mongo_uri = os.environ.get("MONGO_URI", None)
        if self.mongo_uri is None or len(self.mongo_uri.strip()) == 0:
            print("\nA mongodb uri is necessary for the bot to function.\n")
            raise RuntimeError
        self.db = AsyncIOMotorClient(self.mongo_uri).sonus
        self.servers = self.db.servers
        # Startup message
        print('=' * 24)
        print("Sonus")
        print("By: Cyrus")
        print('=' * 24)
        # Load cogs
        for cog in self.loading_cogs:
            print(f"Loading {cog}...")
            try:
                self.load_extension(cog)
                print(f"Successfully loaded {cog}.")
            except Exception as e:
                print(f"Failed to load {cog}. Error: {e}")

    async def get_server(self, server_id: int):
        server_id = str(server_id)
        server = await self.servers.find_one({"_id": server_id})
        if server is None:
            await self.servers.find_one_and_update(
                {"_id": server_id},
                {"$set": {"channels": dict(), "autochannels": dict()}},
                upsert=True,
            )
            server = await self.servers.find_one({"_id": server_id})
        elif type(server["channels"]) is list:
            await self.servers.find_one_and_update(
                {"_id": server_id},
                {"$set": {"channels": dict.fromkeys(map(str, server["channels"])),
                          "autochannels": dict.fromkeys(map(str, server["autochannels"]))}},
                upsert=True,
            )
            server = await self.servers.find_one({"_id": server_id})
        return server

    async def delete_channel(self, server_id: int, channel_id: int, channels: dict):
        server_id = str(server_id)
        channels.pop(str(channel_id))
        await self.servers.find_one_and_update(
            {"_id": server_id},
            {"$set": {"channels": channels}},
            upsert=True,
        )

    async def on_ready(self):
        print('-' * 24)
        print('Logged in as:')
        print(self.user.name + "#" + self.user.discriminator)
        print("Id: " + str(self.user.id))
        print(f"Discord version: {discord.__version__}")
        print(f"Bot version: {__version__}")
        print('-' * 24)
        print("I am logged in and ready!")
        await self.change_presence(activity=discord.Game("@" + self.user.name + " help | v" + __version__))

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            await context.send(f"Command not found. Use `@{context.me.display_name} help` for help.")
        elif isinstance(exception, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(exception, commands.CommandOnCooldown):
            await context.send(f"This command is on cooldown. Try again in {exception.retry_after:.2f}s.")
        elif isinstance(exception, commands.MissingPermissions) or isinstance(exception, commands.NoPrivateMessage) or isinstance(exception, commands.CommandOnCooldown):
            await context.send(exception)
        elif isinstance(exception, commands.CheckFailure):
            await context.send(context.command.checks[0].fail_msg)
        else:
            print("Unexpected exception:", type(exception).__name__ + ":", exception)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        await self.wait_until_ready()
        server = await self.get_server(member.guild.id)
        if before.channel:
            if str(before.channel.id) in server["channels"] and len(before.channel.members) == 0:
                # left auto created channel with no more people
                try:
                    await before.channel.delete()
                except discord.NotFound:
                    # Already deleted
                    pass
                await self.delete_channel(member.guild.id, before.channel.id, server["channels"])
        if after.channel:
            if str(after.channel.id) in server["autochannels"]:
                # joined creating channel
                channel = await after.channel.clone(name="".join(
                    letter for letter in member.display_name if
                    letter not in string.punctuation and letter.isprintable()) + "'s voice call")
                await channel.edit(position=after.channel.position + 1)
                await member.move_to(channel)
                server["channels"][str(channel.id)] = {
                    "creator": member.id,
                    "autochannel": after.channel.id
                }
                await self.servers.find_one_and_update(
                    {"_id": str(member.guild.id)},
                    {"$set": {"channels": server["channels"]}},
                    upsert=True,
                )

    async def on_guild_channel_delete(self, channel):
        server = await self.get_server(channel.guild.id)
        if channel.id in server["autochannels"]:
            del server["autochannels"][str(channel.id)]
            await self.servers.find_one_and_update(
                {"_id": str(channel.guild.id)},
                {"$set": {"autochannels": server["autochannels"]}},
                upsert=True,
            )


bot = Sonus()

token = os.environ.get("TOKEN", None)
if token is None or len(token.strip()) == 0:
    print("\nA bot token is necessary for the bot to function.\n")
    raise RuntimeError
bot.run(token)
