# this is where most of the bullshit will be taking place
import json
import os
import random
import re

import requests

dannybot = os.getcwd()


def unpack_gif(file):
    os.system(
        f'ffmpeg -i "{file}" -vf fps=25 -vsync 0 "{dannybot}\\cache\\ffmpeg\\temp%04d.png" -y')
    return


def repack_gif():
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.png" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}ffmpeg\\output\\palette.png -y')
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.png" -i "{dannybot}ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return


def repack_gif_JPG():
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.jpg" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}ffmpeg\\output\\palette.png -y')
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.jpg" -i "{dannybot}ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return


def cleanup_ffmpeg():
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\{file}')
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg\\output'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\output\\{file}')


def fileCount(folder):
    total = 0  # set total to 0 to begin with
    # recursively walk down the folder passed into the function
    for files in os.walk(folder):

        total += len(files)  # add each file found to total
    return total  # send the total


def ezogaming_regex(datalist, dataentry):
    # ezogaming if you would like to add comments to this catastrophe, be my guest
    # this may even be rewritten completely by the time you are reading this
    with open(f"{dannybot}\\ezogaming\\{datalist}_char") as f:
        entry = f.readlines()
        entry = [x.rstrip() for x in entry]
    with open(f"{dannybot}\\ezogaming\\{datalist}_checker") as f:
        entryalias = f.readlines()
        entryalias = [x.rstrip() for x in entryalias]
    aru = " ".join(dataentry[:])
    inp = re.sub("[^a-z]", "", aru.lower())
    sort = [0] * len(entry)
    for i in range(0, len(entry)):
        sort[i] = i
    random.shuffle(sort)
    for i2 in range(0, len(entry)):
        inputStripped = inp.strip()
        aliasStripped = re.sub(
            "[^a-z]", "", entryalias[sort[i2]].lower().strip())
        entrystripped = re.sub("[^a-z]", "", entry[sort[i2]].lower().strip())
        if (inputStripped in entrystripped) or inputStripped in aliasStripped:
            break
    sort[i2]
    results = entry[sort[i2]]
    return results

#python 3.10 adds switch cases
#
#i am on python 3.8.1 still...
def undertext(name):
    # character overrides
    if name == "danny":
        name = "https://cdn.discordapp.com/attachments/560608550850789377/1005989141768585276/dannyportrait1.png"
    elif name == "danny-funny":
        name = "https://cdn.discordapp.com/attachments/560608550850789377/1005999509496660060/dannyportrait3.png"
    elif name == "danny-angry":
        name = "https://cdn.discordapp.com/attachments/560608550850789377/1005989142825553971/dannyportrait4.png"
    elif name == "danny-pissed":
        name = "https://cdn.discordapp.com/attachments/560608550850789377/1005989142083145828/dannyportrait2.png"
    elif name in ["flashlight", "ezo", "ezogaming"]:
        name = "https://cdn.discordapp.com/attachments/1063552619110477844/1063552733170384926/FFlash.png"
    elif name == "incine":
        name = "https://cdn.discordapp.com/attachments/1063552619110477844/1063552737435992084/FIncine.png"
    elif name == "pizzi":
        name = "https://cdn.discordapp.com/attachments/1063552619110477844/1063552743626780732/FPizzi.png"
    elif name == "cris":
        name = "https://cdn.discordapp.com/attachments/1063552619110477844/1063552816397951037/FCris.png"
    elif name == "seki":
        name = "https://cdn.discordapp.com/attachments/1063552619110477844/1063738177212399658/sekiportrait1.png"
    else:
        name = name

    # link overrides
    if name.startswith("https://"):
        name = "custom&url=" + name
    return name

def gettenor(url=''):
    apikey = "8FMRE051ZV31"
    gifid = url[url.rindex('-')+1:]
    r = requests.get(
        "https://api.tenor.com/v1/gifs?ids=%s&key=%s&media_filter=minimal" % (gifid, apikey))

    if r.status_code == 200:
        gifs = json.loads(r.content)
    else:
        gifs = None
    return gifs['results'][0]['media'][0]['gif']['url']

#idk how any of this shit works
#ezogaming wrote all of this
async def message_history_img_handler(ctx):
    channel = ctx.message.channel
    extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'gif','PNG', 'JPG', 'JPEG', 'GIF', 'BMP', 'WEBP', 'GIF']
    async for msg in channel.history(limit=500):
        if len(msg.attachments) > 0:
            ext = msg.attachments[0].url.split('.')[-1]
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            if 'https://tenor.com/view/' in msg.content:
                a = (str(gettenor(msg.content)))
                return a
            else:
                aa = str(msg.content)
                ext = aa.split('.')[-1]
                if ext in extensions:
                    a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                    a = a.split('?')[0]
                    return a


async def message_history_audio_handler(ctx):
    channel = ctx.message.channel
    extensions = ['wav', 'ogg', 'mp3', 'flac', 'aiff', 'opus', 'm4a', 'oga', 'WAV', 'OGG', 'MP3', 'FLAC', 'AIFF', 'OPUS', 'M4A', 'OGA']
    async for msg in channel.history(limit=500):
        if len(msg.attachments) > 0:
            ext = msg.attachments[0].url.split('.')[-1]
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            aa = str(msg.content)
            ext = aa.split('.')[-1]
            if ext in extensions:
                a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                a = a.split('?')[0]
                return a


async def message_history_video_handler(ctx):
    channel = ctx.message.channel
    extensions = ['mp4', 'avi', 'mpeg', 'mpg', 'webm', 'mov', 'mkv', 'MP4', 'AVI', 'MPEG', 'MPG', 'WEBM', 'MOV', 'MKV']
    async for msg in channel.history(limit=500):
        if len(msg.attachments) > 0:
            ext = msg.attachments[0].url.split('.')[-1]
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            aa = str(msg.content)
            ext = aa.split('.')[-1]
            if ext in extensions:
                a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                a = a.split('?')[0]
                return a