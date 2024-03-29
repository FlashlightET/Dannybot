# most of these are APIs

# if you can't find a variable used in this file its probably imported from here
from config import *

# this shit is kind of dumb i wanna find a better way to do this - FDG
global request_is_processing
request_is_processing = False

class ai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Interact with GPT3 using Dannybot.", brief="Get AI generated text based on provided prompts")
    async def write(self, ctx, *, prompt):
        gpt_prompt = str(f"write me {prompt}")
        print(gpt_prompt)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=gpt_prompt,
            temperature=random.uniform(0., 1.0),
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        await ctx.reply(response['choices'][0]['text'], mention_author=True)
        
    @commands.command(description="Interact with GPT3 using Dannybot.", brief="Get AI generated text based on provided prompts")
    async def gpt(self, ctx, temp: typing.Optional[float] = 0.7, *, prompt):
        gpt_prompt = str(prompt)
        print(gpt_prompt)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=gpt_prompt,
            temperature=temp,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=1.0,
            presence_penalty=0.0
        )
        await ctx.reply(response['choices'][0]['text'], mention_author=True)
        
    @commands.command(aliases=['code'],  description="Interact with GPT3-Code using Dannybot.", brief="Get AI generated code based on provided prompts")
    async def python(self, ctx, *, prompt):
        await ctx.send("This command is temporarily disabled.")
        return
        response = openai.Completion.create(
        model="code-davinci-002",
        prompt= f"\"\"\"\n{prompt}\n\"\"\"\n",
        temperature=0.2,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=2.0,
        presence_penalty=0
        )
        
        with open(f'{dannybot}\\cache\\code.py', 'w', encoding="utf-8") as f:
            f.write(response['choices'][0]['text'])
            f.close
        with open(f'{dannybot}\\cache\\code.py', 'rb') as f:
            await ctx.reply(file=File(f, 'code.py'), mention_author=True)
            f.close

    @commands.command(aliases=['upscale'], description="Locally run waifu2x using speed-optimized settings and send the results.", brief="Upscale images using waifu2x")
    async def waifu(self, ctx, *args):
        cmd_info = await resolve_args(ctx, args, ctx.message.attachments)
        Link_To_File = cmd_info[0]
        await ctx.send("Upscaling. Please wait...")
        with open(f'{dannybot}\\cache\\w2x_in.png', 'wb') as f:
            f.write(requests.get(Link_To_File).content)
            f.close
        os.system(f"{Waifu2x} -i {dannybot}\\cache\\w2x_in.png -o {dannybot}\\cache\\w2x_out.png -m noise_scale --scale_ratio 2 --noise_level 2 -x")
        with open(f'{dannybot}\\cache\\w2x_out.png', 'rb') as f:
            await ctx.reply(file=File(f, 'waifu2x.png'))
        f.close

    @commands.command(aliases=['15', '15tts'], description="Sends AI sentences using a very real and legitimate 15.ai API.", brief="Use 15.ai to generate funny sentences")
    async def fifteen(self, ctx, *, msg):
        def check(msg):
            return msg.author == ctx.author
        global request_is_processing
        blacklist = [1, 2]
        if ctx.author.id in blacklist:
            await ctx.send("You've been blacklisted from this command")
            return
        else:
            if request_is_processing is True:
                await ctx.reply(
                    "Please allow the previous synthesis to finish.",
                    delete_after=10,
                    mention_author=True,
                )
                return
            try:
                await ctx.send('Which voice would you like? (It is case sensitive!)')
                msgfunc = await self.client.wait_for("message", check=check, timeout=30)
                requested_speaker = msgfunc.content
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you didn't reply in time!")
                return
            await ctx.send("Processing... This could take a while...")
            request_is_processing = True
        FifteenAPI().save_to_file(f"{requested_speaker}", f"{msg}", f"{dannybot}\\cache\\15_output.wav")
        await ctx.reply(file=discord.File(f"{dannybot}\\cache\\15_output.wav"), mention_author=True)
        await ctx.send("This command is powered by 15.ai ^^^ https://twitter.com/fifteenai")
        request_is_processing = False
        return

    @commands.command(aliases=['quote'], description="Sends AI generated quotes using the inspirobot API.", brief="Get AI generated inspirational posters")
    async def inspire(self, ctx):
        link = "http://inspirobot.me/api?generate=true"
        f = requests.get(link)
        File_Url = f.text
        img = PIL.Image.open(requests.get(File_Url, stream=True).raw)
        img.save(f"{dannybot}\\cache\\quote.jpg", "JPEG")
        f = discord.File(f"{dannybot}\\cache\\quote.jpg", filename="quote.jpg")
        embed = discord.Embed(color=0xffc7ed)
        embed.set_image(url="attachment://quote.jpg")
        embed.set_footer(text="Powered by https://inspirobot.me/")
        await ctx.reply(file=f, embed=embed, mention_author=True)

    @commands.command(aliases=['pngify', 'transparent'], description="Runs the provided image through a (free) API call to remove.bg, to make the image transparent.", brief="Remove the background from an image using AI")
    async def removebg(self, ctx, *args):
        cmd_info = await resolve_args(ctx, args, ctx.message.attachments)
        Link_To_File = cmd_info[0]
        await ctx.send("Removing background. Please wait...", delete_after=5)
        with open(f'{dannybot}\\cache\\removebgtemp.png', 'wb') as f:
            f.write(requests.get(Link_To_File).content)
            f.close
        response = requests.post("https://api.remove.bg/v1.0/removebg", data={"image_url": str(Link_To_File), "size": "auto"}, headers={"X-Api-Key": os.getenv("REMOVEBG_KEY")},)
        if response.status_code == requests.codes.ok:
            with open(f'{dannybot}\\cache\\removebg.png', 'wb') as out:
                out.write(response.content)
                f.close
            with open(f'{dannybot}\\cache\\removebg.png', 'rb') as f:
                await ctx.reply(file=File(f, 'removed.png'), mention_author=True)
                f.close
        else:
            await ctx.reply("Processing of the image failed. This is most likely because no background was detected.", mention_author=True)
            print(response.content)

    @commands.command(description="Uses the craiyon API to send user prompts and return AI generated output.", brief="Use craiyon to create AI generated images")
    async def dalle(self, ctx, *, prompt):
        # rotty shit, this is the main function that runs when the command is called
        images = None
        attempt = 0
        print("-------------------------------------")
        print(f'Dalle command ran with prompt "{prompt}"')
        # this while loop is to make sure that the image generation request is successful
        while not images:
            if attempt > 0:
                print(
                    f'Image generate request failed on attempt {attempt} for prompt "{prompt}"'
                )
            attempt += 1
            # this is the function that sends the request to the craiyon API
            images = await generate_images(prompt)
            print(
                f'Successfully started image generation with prompt "{prompt}" on attempt {attempt}'
            )
            prompt_hyphenated = prompt.replace(" ", "-")
            # this is the function that makes the collage
            collage = await make_collage(images, 3)
            b = collage
            collage = discord.File(
                collage, filename=f"{prompt_hyphenated}.{DALLE_FORMAT}")
            print("Sending image...")
            await ctx.reply(file=collage, mention_author=True)
            print("Caching image...")
            with open(f"{dannybot}\\cache\\dalle.png", "wb") as f:
                b.seek(0)
                f.write(b.read())
                f.close
                print("Image Cache successful")
                print("-------------------------------------")

async def setup(bot: commands.Bot):
    await bot.add_cog(ai(bot))