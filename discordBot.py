# this is the file that boots up every other file.
# should really shouldnt need to touch this file ever

# if you can't find a variable used in this file its probably imported from here
from config import *

# make it look nice in the console
print("-----------------------------------------")
print("DANNYBOT IS STARTING UP... PLEASE WAIT...")
print("-----------------------------------------")

# asyncio bad btw
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# define our prefix(es) and status
bot = commands.Bot(
    command_prefix=(dannybot_prefixes),
    status=discord.Status.online,
    activity=discord.Activity(name="Muse Dash", type=1),
    intents=discord.Intents.all(),
)

# do this when everything else is done
@bot.event
async def on_ready():
    # print a success message upon boot
    print("---------------------------------------------------------------------")
    print(f"{bot.user} successfully booted on discord.py version {discord.__version__}")
    print("---------------------------------------------------------------------")
    return

# this is our message handler
@bot.event
async def on_message(input):
    # teehee funny chance for the bot to just say no
    if random.randint(0, dannybot_denialRatio) == dannybot_denialRatio and any(input.content.startswith(prefix) for prefix in dannybot_prefixes):
        await input.channel.send(random.choice(dannybot_denialResponses), reference=input)
    else:
        os.chdir(f"{dannybot}") # always make sure we're in dannybots directory
        await bot.process_commands(input)

# this is a ping command and it's pretty self-explanatory
@bot.command(description="Calculate bot latency using time.monotonic(), and send the results.", brief="Sends the current bot latency")
async def ping(ctx):
    before = time.monotonic()
    message = await ctx.send("Ping is...")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f"Ping is {int(ping)}ms")
    print(f'Dannybot was pinged at {int(ping)}ms')

# say command because every good bot should be a vessel for its creator to speak through - FDG
@bot.command(hidden=True)
@commands.is_owner()
async def say(ctx, *, args):
    await ctx.send(args)
    # delete the command message, leaving only what Dannybot sends
    await ctx.message.delete()

# theres definitely a better way to do this
@bot.command(description="Delete the most recent command output in the current channel. This only affects Dannybot.", brief="Undo the last command output")
async def undo(ctx):
    channel = ctx.message.channel
    async for msg in channel.history(limit=500):
        if msg.author.id == 847276836172988426:
            await msg.delete()
            return

# this command reloads a specified cog. used for testing, you can call this command to update code on a cog without restarting the whole bot
@bot.command(description="This is an owner only command. It allows for any module to be reloaded on the fly.", brief="Debug tool for modules")
@commands.is_owner()
async def reload(ctx, module):
    if module == "all":
        for filename in [f for f in os.listdir("./cogs") if f.endswith(".py")]:
            await bot.unload_extension(f"cogs.{filename[:-3]}")
            await bot.load_extension(f"cogs.{filename[:-3]}")
        await ctx.send("Reloaded all modules!")
    else:
        await bot.unload_extension(f"cogs.{module}")
        await bot.load_extension(f"cogs.{module}")
        await ctx.send(f"Reloaded {module} module!")

# this clears the cache manually in case you need to do it with the bot still up
@bot.command(description="This is an owner only command. It clears Dannybots cache of all temporary files.", brief="Clears Dannybots cache")
@commands.is_owner()
async def cache(ctx):
    for file in os.listdir(f'{dannybot}\\cache'):
        if 'git' not in file and '.' in file:
            os.remove(f'{dannybot}\\cache\\{file}')
            print(f"deleted {dannybot}\\cache\\{file}")
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\{file}')
            print(f'deleted{dannybot}\\cache\\ffmpeg\\{file}')
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg\\output'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\output\\{file}')
            print(f'deleted{dannybot}\\cache\\ffmpeg\\{file}')
    await ctx.send("Cache cleared!")

# stage all of our cogs
async def load_extensions():
    for filename in [f for f in os.listdir("./cogs") if f.endswith(".py")]:
        await bot.load_extension(f"cogs.{filename[:-3]}")
        print("imported module: " + f"{filename[:-3]}")

# run all of our startup tasks including loading all cogs, and clearing the cache if enabled
async def main():
    async with bot:
        if cache_clear_onLaunch:
            print("clearing cache from previous session...")
            clear_cache()
            print("-----------------------------------------")
        await load_extensions()
        await bot.start(dannybot_token)

asyncio.run(main())