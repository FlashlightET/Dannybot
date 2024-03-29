# this is where most of the bullshit will be taking place
# anything you need to configure will be located in here

# ----------
# Imports
# ----------

import asyncio
import base64
import hashlib
import io
import json
import os
import random
import re
import string
import sys
import time
import traceback
import typing
import urllib
import urllib.request
from collections import namedtuple
from textwrap import wrap

import aiohttp
import discord
import furl
import numpy
import openai
import PIL
import requests
#import revolt
from discord import File, app_commands
from discord.ext import commands
from dotenv import load_dotenv
from petpetgif import petpet
from PIL import (GifImagePlugin, Image, ImageColor, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps, ImageSequence)
#from revolt.ext import commands
from wand.image import Image as magick

from fifteen import FifteenAPI

load_dotenv()

# ----------
# Variables
# ----------

# dannybot config
dannybot_prefixes = ["d.", "#", "D.", "ratio + "] #bot prefix(es)
dannybot_token = os.getenv("TOKEN") #token
dannybot_token_revolt = os.getenv("REVOLT_TOKEN") #revolt token
dannybot_denialRatio = 250 # chance for dannybot to deny your command input
dannybot_denialResponses = ['no', 'no.', 'nah', 'nope', 'no thanks'] # what dannybot says upon denial
dannybot = os.getcwd() # easy to call variable that stores our current working directory
cache_clear_onLaunch = True # dannybot will clear his cache on launch if set to true
logs_channel = 971178342550216705 # channel to log commands
database_acceptedFiles = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov'] # list of accepted files for the bots public database

#configs for the image manipulation commands
imageLower = 250 # the smallest image width image commands will use. if the image is thinner than this, it will proportionally scale to this size
imageUpper = 1500 # the largest image width image commands will use. if the image is wider than this, it will proportionally scale to this size

# .env
openai.api_key = os.getenv("OPENAI_API_KEY")
removebg_key = os.getenv("REMOVEBG_KEY")
tenor_apikey =  os.getenv("TENOR_KEY")

# external paths
KemonoFriendsPath = "I:\\Anime\\Kemono Friends" # put your kemono friends regex files into here
NekoparaPath = "I:\\Anime\\Nekopara" # put your nekopara regex files into here
MimiPath = "I:\\Anime\\Kemono girls" # put your animal girl files here
PicturesPath = "C:\\Users\\weebm\\Pictures" # set this to your pictures folder
VideosPath = "C:\\Users\\weebm\\Videos\\epic" # set this to your videos folder
GifsPath = "C:\\Users\\weebm\\Pictures\\GIFS" # set this to your gifs folder

# internal paths
Cookies = f"{dannybot}\\assets" # set this to your YT-DL cookies folder
UltimateVocalRemover = f"{dannybot}\\tools\\UltimateVocalRemover" # set this to the path of your install of UltimateVocalRemover
Waifu2x = f"{dannybot}\\tools\\waifu2x-caffe\\waifu2x-caffe-cui.exe" # set this to the path of your waifu2x-caffe-cui.exe file in your waifu2x-caffe install

# 8ball responses for the 8ball command
ball_responses = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful."
]

# logo list for the logo command
logolist = [
    "clan",
    "neon",
    "fluffy",
    "water",
    "smurfs",
    "style",
    "runner",
    "blackbird",
    "fabulous",
    "glow",
    "chrominium",
    "amped",
    "supermarket",
    "crafts",
    "fire",
    "steel",
    "glossy",
    "fifties",
    "retro",
    "beauty",
    "birdy",
    "inferno",
    "winner",
    "uprise",
    "global",
    "silver",
    "minions",
    "magic",
    "fancy",
    "orlando",
    "fortune",
    "swordfire",
    "roman",
    "golden",
    "outline",
    "funtime",
]

# this is for the undertext command
deltarune_dw = [
    'ralsei',
    'lancer',
    'king', 'jevil',
    'queen',
    'spamton',
    "clyde",
    "lori",
    "rhombo"
]


# dalle shit
DALLE_API = "https://backend.craiyon.com/generate"
DALLE_FORMAT = "png"

# ----------
# Functions
# ----------

# take a provided gif file and unpack each frame to /cache/ffmpegs
def unpack_gif(file):
    print("unpacking gif...")
    os.system(f'ffmpeg -i "{file}" -vf fps=25 -vsync 0 "{dannybot}\\cache\\ffmpeg\\temp%04d.png" -y')
    return

# take each frame in /cache/ffmpeg/out and turn it back into a gif
def repack_gif():
    print("generating palette...")
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}\\cache\\ffmpeg\\output\\palette.png -y')
    print("repacking gif...")
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png" -i "{dannybot}\\cache\\ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return

# take each frame in /cache/ffmpeg/out and turn it back into a gif (jpg variant)
def repack_gif_JPG():
    print("generating palette...")
    print("repacking gif (jpg)...")
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.jpg" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}\\cache\\ffmpeg\\output\\palette.png -y')
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.jpg" -i "{dannybot}\\cache\\ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return

# clear the ffmpeg and ffmpeg/output folders of any residual files
def cleanup_ffmpeg():
    print("cleaning up...")
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\{file}')
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg\\output'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\output\\{file}')
            
# generate a random hexadecimal string
def randhex(bits):
    return hashlib.sha256(str(random.getrandbits(bits)).encode('utf-8')).hexdigest()

# clear the cache folder of all files
def clear_cache():
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
    return

# get the amount of files in a folder
def fileCount(folder):
    return sum(len(filenames) for dirpath, dirnames, filenames in os.walk(folder))

# get the total size of all files in a folder
def fileSize(folder):   
    # get the file size
    total_size = sum(os.path.getsize(os.path.join(dirpath, f)) for dirpath, dirnames, filenames in os.walk(folder) for f in filenames) 
    # for loop to convert file size to bytes, KB, MB, GB, TB
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        # if file size is less than 1024 bytess
        if total_size < 1024.0:
            # return file size and type
            return "%3.1f %s" % ( total_size, x)
        # divide file size by 1024
        total_size /= 1024.0
    return total_size

# overcomplicated function for parsing and matching data with a list of aliases
# NEVER TRY TO COMMENT EZOGAMING CODE - FDGs
def ezogaming_regex(datalist, dataentry):
    # open the file with the list of entries
    with open(f"{dannybot}\\ezogaming\\{datalist}_char") as f: entry = [x.rstrip() for x in f.readlines()]
    # open the file with the list of aliases
    with open(f"{dannybot}\\ezogaming\\{datalist}_char") as f: entryalias = [x.rstrip() for x in f.readlines()]
    # remove all non-alphabetic characters from the input
    inp = re.sub("[^a-z]", "", " ".join(dataentry[:]).lower())
    # create a list of the same length as the list of entries
    sort = [0] * len(entry)
    # fill the list with the index of the entry
    for i in range(0, len(entry)):
        sort[i] = i
    # shuffle the list
    random.shuffle(sort)
    # for each entry in the list
    for i2 in range(0, len(entry)):
        # remove all non-alphabetic characters from the input, entry, and aliases
        inputStripped = inp.strip()
        aliasStripped = re.sub("[^a-z]", "", entryalias[sort[i2]].lower().strip())
        entrystripped = re.sub("[^a-z]", "", entry[sort[i2]].lower().strip())
        # if a match is found between the input with the entry OR alias
        if (inputStripped in entrystripped) or inputStripped in aliasStripped:
            # stop the loop
            break
    # get the index of the entry
    sort[i2]
    # get the entry
    results = entry[sort[i2]]
    return results

def undertext(name, text, isAnimated):
    
    # animated override: if the name contains "animated-", remove it and set isAnimated to True
    if "animated-" in name:
        name = name.replace("animated-","")
        isAnimated = True
    
    # AU style overrides: if the name contains a valid AU, add the AU style to the name and text
    if "uf" in name: # underfell
        name = f"{name}&boxcolor=b93b3c&asterisk=b93b3c&charcolor=b93b3c"
        text = f"color=%23b93b3c%20{text}"
    if name in deltarune_dw: # deltarune
        name = f"{name}&box=deltarune&mode=darkworld"
    
    # character overrides: replace underscores with dashes, then use the dictionary to replace the name with the link
    name = (lambda name: {
        "danny": "https://cdn.discordapp.com/attachments/560608550850789377/1005989141768585276/dannyportrait1.png",
        "danny-funny": "https://cdn.discordapp.com/attachments/560608550850789377/1005999509496660060/dannyportrait3.png",
        "danny-angry": "https://cdn.discordapp.com/attachments/560608550850789377/1005989142825553971/dannyportrait4.png",
        "danny-pissed": "https://cdn.discordapp.com/attachments/560608550850789377/1005989142083145828/dannyportrait2.png",
        "crackhead": "https://cdn.discordapp.com/attachments/1063552619110477844/1076067803649556480/image.png",
        "pizzi": "https://cdn.discordapp.com/attachments/1063552619110477844/1082228005256044575/pizziportrait1.png",
        "pizzi-stare": "https://cdn.discordapp.com/attachments/1063552619110477844/1082228014856814612/pizziportrait2.png",
        "pizzi-scream": "https://cdn.discordapp.com/attachments/1063552619110477844/1082228022796615720/pizziportrait3.png",
        "sam": "https://cdn.discordapp.com/attachments/1063552619110477844/1082220603387428894/samportrait1.png",
        "flashlight": "https://cdn.discordapp.com/attachments/1063552619110477844/1068251386430619758/image.png",
        "ezo": "https://cdn.discordapp.com/attachments/1063552619110477844/1068251386430619758/image.png",
        "ezogaming": "https://cdn.discordapp.com/attachments/1063552619110477844/1068251386430619758/image.png",
        "incine": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552737435992084/FIncine.png",
        "cris": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552816397951037/FCris.png",
        "seki": "https://cdn.discordapp.com/attachments/1063552619110477844/1063738177212399658/sekiportrait1.png",
        "seki-eyes": "https://cdn.discordapp.com/attachments/560608550850789377/1075684786489798696/sekiportrait2.png",
        "seki-evil": "https://cdn.discordapp.com/attachments/1063552619110477844/1075687740793946122/sekiportrait3.png",
        "leffrey" : "https://cdn.discordapp.com/attachments/886788323648094219/1068253912919982100/image.png",
        "reimu-fumo" : "https://cdn.discordapp.com/attachments/1063552619110477844/1082233613040504892/image.png",
        "suggagugga" : "https://cdn.discordapp.com/attachments/1063552619110477844/1068248384164614154/mcflurger.png"
    }.get(name, name))(name)

    # link overrides: if the name starts with "https://", add "custom&url=" to the beginning of the name
    if name.startswith("http"):
        name = f"custom&url={name}"
    
    # text overrides: modify the box and text display based on passed parameters
    if "font=wingdings" in text:
        name = f"{name}&asterisk=null"
    
    # finalizing: set the name and text to the name and text, then return the name, text, and isAnimated
    name = name
    #replacing the discord double underscore shit with spaces
    text = text.replace("_ _", "%20")
    return name, text, isAnimated

# grab the gif url of a tenor id using the tenor api
def gettenor(gifid=None):
    # get the api key from the config file
    apikey = tenor_apikey
    r = requests.get(
        "https://api.tenor.com/v1/gifs?ids=%s&key=%s&media_filter=minimal" % (gifid, apikey))

    if r.status_code == 200:
        gifs = json.loads(r.content)
    else:
        gifs = None
    return gifs['results'][0]['media'][0]['gif']['url']

# go through the last 500 messages sent in the channel a command is ran in and check for correpsonding files
async def message_history_handler(ctx, type):
    channel = ctx.message.channel
    #determine required extensions
    match type:
        case "image":
            extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
        case "audio":
            extensions = ['wav', 'ogg', 'mp3', 'flac', 'aiff', 'opus', 'm4a','oga']
        case "midi":
            extensions = ['mid', 'midi']
        case "video":
            extensions = ['mp4', 'avi', 'mpeg', 'mpg', 'webm', 'mov','mkv']          
    async for msg in channel.history(limit=500):
        if type == "images":
            # if the message contains an attachment, check if it's an image and return the url
            if msg.attachments:
                ext = msg.attachments[0].url.split('.')[-1].lower()
                if ext in extensions:
                    return msg.attachments[0].url
            else:
                    # if the message contains a tenor link, get the tenor id and return the gif
                    if 'https://tenor.com/view/' in msg.content:
                        for x in re.finditer(r"tenor\.com/view/.*-(\d+)", str(msg.content)):
                            tenorid = x.group(1)
                        return (str(gettenor(tenorid)))
                    ext = str(msg.content).split('.')[-1].lower()
                    if ext in extensions:
                        return re.findall("(?=http).*?(?= |\n|$)", msg.content)[0].split('?')[0]
        else:
            if msg.attachments:
                ext = msg.attachments[0].url.split('.')[-1].lower()
                if ext in extensions:
                    return msg.attachments[0].url
            if 'http' in msg.content:
                aa = str(msg.content)
                ext = aa.split('.')[-1]
                if ext in extensions:
                    a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                    a = a.split('?')[0]
                    return a

# extracts url/arguments from a command
async def resolve_args(ctx, args, attachments, type = "image"):
    try:
        if 'http' in args[0]: #see if first in the list of "args" is a URL
            #Case of "d.meme http://balls.com/balls.png balls|balls"
            return [args[0].split('?')[0], ' '.join(args[1:])] #everything after that is set as the text and combined to a string
        elif attachments: #otherwise check if there are attachments
            #Case of "d.meme balls|balls" with attached file
            return [attachments[0].url.split('?')[0], ' '.join(args)] #the command text is everything in the args since there is no url as the first arg
        else: #if there are no attachments or a link, run the context handler
            #Case of "d.meme balls|balls" with no attachment
            return [await message_history_handler(ctx, type), ' '.join(args)]
    except IndexError: #this happens whem there is no args[0] because the command was simply, say, "d.explode" with no arguments.
        if attachments: #check if there are attachments
            #Case of "d.meme balls|balls" with attached file
            return [attachments[0].url.split('?')[0], ' '.join(args)] #get everything leading up to "?width=500"-type shenenigans
        else: #if there are no attachments or a link, run the context handler
            #Case of "d.meme balls|balls" with no attachment
            return [await message_history_handler(ctx, type), ' '.join(args)]

# deepfry an image
def deepfry(inputpath, outputpath):
    # open image
    image = PIL.Image.open(f'{inputpath}').convert('RGB')
    image.save(f'{dannybot}\\cache\\deepfry_in.jpg', quality=15)
    with magick(filename=f'{dannybot}\\cache\\deepfry_in.jpg') as img:
        # apply deepfry
        img.level(0.2, 0.9, gamma=1.1)
        img.level(0.2, 0.9, gamma=1.1)
        img.sharpen(radius=8, sigma=4)
        img.noise("laplacian", attenuate=1.0)
        img.level(0.2, 0.9, gamma=1.1)
        img.sharpen(radius=8, sigma=4)
        img.save(filename=f'{outputpath}')
    return

# resize image to fit within bounds
def imagebounds(path):
    # open image and get size
    image = PIL.Image.open(path)
    width, height = image.size

    # if image is smaller than lower cap
    if width < imageLower:
        # resize image and save
        image.resize((imageLower, int(height * (imageLower/float(width)))), Image.Resampling.LANCZOS).save(path)

    # if image is larger than upper cap
    elif width > imageUpper:
        # resize image and save
        image.resize((imageUpper, int(height * (imageUpper/float(width)))), Image.Resampling.LANCZOS).save(path)

# primary function of the meme command
# take an image and put centered and outlined impact font text with a black outline over the top and bottom of the image
# this is stolen from a, like, decade old repo
def make_meme(Top_Text, Bottom_Text, path):
    img = PIL.Image.open(path)

    imagebounds(path)
    img = PIL.Image.open(path) # reopen the image
        
    # scale and position the text
    fontSize = int(img.size[0])
    font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
    topTextSize = font.getsize(Top_Text)
    bottomTextSize = font.getsize(Bottom_Text)
    
    # find the biggest font size that works, and then make sure its at least 1
    while topTextSize[0] > img.size[0]-20 or bottomTextSize[0] > img.size[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
        topTextSize = font.getsize(Top_Text)
        bottomTextSize = font.getsize(Bottom_Text)
    if fontSize  <= 0:
        fontSize = 1
    
    # center and position the text
    topTextPositionX = (img.size[0]/2) - (topTextSize[0]/2)
    topTextPosition = (topTextPositionX, 0)
    bottomTextPositionX = (img.size[0]/2) - (bottomTextSize[0]/2)
    bottomTextPositionY = img.size[1] - bottomTextSize[1]
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY - 10)

    # FIXED THE FUCKING STROKE SIZE - FDG
    # it divides the size of top text by 75 and uses that as the stroke size
    # also we make sure the stroke size is AT LEAST 1
    outline = int((topTextSize[0]//110) + bottomTextSize[0]//110)
    if outline <= 0:
        outline = 1

    # draw the text
    draw = ImageDraw.Draw(img)
    draw.text(topTextPosition, Top_Text, (255, 255, 255), font=font,
              stroke_width=outline, stroke_fill=(0, 0, 0))
    draw.text(bottomTextPosition, Bottom_Text, (255, 255, 255),
              font=font, stroke_width=outline, stroke_fill=(0, 0, 0))

    # save the resulting image
    img.save(f"{dannybot}\\cache\\meme_out.png")
    return

# gif version
def make_meme_gif(Top_Text, Bottom_Text):

    # iterate through every frame in the ffmpeg folder and edit them
    for frame in os.listdir(f"{dannybot}\\cache\\ffmpeg\\"):
        if '.png' in frame:

            # open image in PIL
            img = PIL.Image.open(f"{dannybot}\\cache\\ffmpeg\\{frame}")
            path = f"{dannybot}\\cache\\ffmpeg\\{frame}"

            imagebounds(path)
            img = PIL.Image.open(path) # reopen the image
                
            # scale and position the text
            fontSize = int(img.size[0])
            font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
            topTextSize = font.getsize(Top_Text)
            bottomTextSize = font.getsize(Bottom_Text)
            
            # find the biggest font size that works, and then make sure its at least 1
            while topTextSize[0] > img.size[0]-20 or bottomTextSize[0] > img.size[0]-20:
                fontSize = fontSize - 1
                font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
                topTextSize = font.getsize(Top_Text)
                bottomTextSize = font.getsize(Bottom_Text)
            if fontSize  <= 0:
                fontSize = 1
            
            # center and position the text
            topTextPositionX = (img.size[0]/2) - (topTextSize[0]/2)
            topTextPosition = (topTextPositionX, 0)
            bottomTextPositionX = (img.size[0]/2) - (bottomTextSize[0]/2)
            bottomTextPositionY = img.size[1] - bottomTextSize[1]
            bottomTextPosition = (bottomTextPositionX, bottomTextPositionY - 10)

            # FIXED THE FUCKING STROKE SIZE - FDG
            # it divides the size of top text by 75 and uses that as the stroke size
            # also we make sure the stroke size is AT LEAST 1
            outline = int((topTextSize[0]//110) + bottomTextSize[0]//110)
            if outline <= 0:
                outline = 1

            # draw the text
            draw = ImageDraw.Draw(img)
            draw.text(topTextPosition, Top_Text, (255, 255, 255), font=font,
                    stroke_width=outline, stroke_fill=(0, 0, 0))
            draw.text(bottomTextPosition, Bottom_Text, (255, 255, 255),
                    font=font, stroke_width=outline, stroke_fill=(0, 0, 0))

            # save the resulting image
            img.save(f"{dannybot}\\cache\\ffmpeg\\output\\{frame}")
    repack_gif()

    return

# dalle shit
# rotty wrote the following three and I don't feel like reading through it and commenting everything - FDG

# communicate with the dalle API and ask it to generate our prompt
async def generate_images(prompt: str) -> str(io.BytesIO):
    async with aiohttp.ClientSession() as session:
        async with session.post(DALLE_API, json={"prompt": prompt}) as response:
            if response.status == 200:
                print("Dalle server is OK")
                response_data = await response.json()
                images = [
                    io.BytesIO(base64.decodebytes(bytes(image, "utf-8")))
                    for image in response_data["images"]
                ]
                return images
            else:
                return None

# generate the images for dalles 3x3 grid
def make_collage_sync(images: str(io.BytesIO), wrap: int) -> io.BytesIO:
    image_arrays = [numpy.array(PIL.Image.open(image)) for image in images]
    image_ct = 1
    for image in images:
        print(str(image_ct) + " image(s) generated out of " + "9")
        image_ct += 1
        image.seek(0)
    collage_horizontal_arrays = [
        numpy.hstack(image_arrays[i: i + wrap])
        for i in range(0, len(image_arrays), wrap)
    ]
    collage_array = numpy.vstack(collage_horizontal_arrays)
    collage_image = Image.fromarray(collage_array)
    collage = io.BytesIO()
    collage_image.save(collage, format=DALLE_FORMAT)
    print("Attempting to generate 3x3")
    collage.seek(0)
    return collage

# assemble and save the image grid
async def make_collage(images: str(io.BytesIO), wrap: int) -> io.BytesIO:
    images = await asyncio.get_running_loop().run_in_executor(
        None, make_collage_sync, images, wrap
    )
    print("3x3 Generated")
    return images

# generate list from directory of files
def listgen(directory):
    list =  os.listdir(directory)
    string = ', '.join(list)
    return string

# REVOLT ONLY FUNCTIONS