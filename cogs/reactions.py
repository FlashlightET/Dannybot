# log command usage to the console and to a specified channel

# if you can't find a variable used in this file its probably imported from here
from config import *


class reactions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, input: discord.Message):
        if {talking_channel} not in str(input.channel.name) and not input.author.bot:
            if "dannybot" in input.content.lower():
                await input.channel.send("me", reference=input)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(reactions(bot))
