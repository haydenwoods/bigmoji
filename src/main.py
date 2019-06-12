# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import urllib
import sys
import os
from math import sqrt
import discord
from discord.ext import commands
import datetime
import aiohttp        
import aiofiles
from PIL import Image, ImageChops
import math

MAXCHARS = 200
DEFAULTEMOJI = "⬜"
AVERAGEWEIGHT = 0.5
POPULARWEIGHT = 0.3
VISIBLEWEIGHT = 0.2

client = commands.Bot(command_prefix='!')
max_width = int(os.environ["MAX_WIDTH"])

#Discord Events
@client.event
async def on_ready():
  game = discord.Game("games just like Karen smh")
  await client.change_presence(status=discord.Status.online, activity=game)
  print("Logged in as %s (%s)" % (client.user.name, client.user.id))

@client.event
async def on_message(message):
  #Dont accept attachments from itself
  if message.author == client.user:
    return

  #Keep at end
  await client.process_commands(message)

#Discord Commands
@client.command()
async def generate(ctx, w, flag=None, avw=AVERAGEWEIGHT, pw=POPULARWEIGHT, vw=VISIBLEWEIGHT):
  #Error checking
  err = ""
  if int(width) > 80:
    err = "You want me to crash, do yah?"
  if len(ctx.message.attachments) != 1:
    err = "Mate... gonna have to give me an image"
  if err != "":
    await ctx.send(err)
    return
  
  width = int(w)
  weight = (avw, pw, vw)
  filename = str(datetime.datetime.utcnow().timestamp())
  
  try:
    os.mkdir("temp")
  except:
    pass

  try:
    imagefile = "temp/%s.%s" % (filename, image.split(".")[-1])  
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(image) as resp:
          if resp.status == 200:
            f = await aiofiles.open(imagefile, mode='wb')
            await f.write(await resp.read())
            await f.close()
    except Exception as e:
      print(e)
    
    if width < max_width:
      await ctx.send("Gimme two secs...")
      msg = makeImage(imagefile, width, True, weight)
      l = msg.split("\n")
      linepermessage = 200//width

      print(l)
      for i in range(int(len(l)/linepermessage)):
        await ctx.send("\n".join(l[i*linepermessage:(i+1)*linepermessage]))
    else:
      await ctx.send("You want me to crash, do yah?")
  except Exception as e:
    print(e)

#Functions
def makeImage(file=None, width=None, ret=False, weight=(0.6,0.3,0.1)):
  if not file:
    file = sys.argv[1]
  if not width:
    width = int(sys.argv[2])
  if not weight:
    weight = (AVERAGEWEIGHT, POPULARWEIGHT, VISIBLEWEIGHT)

  datafile = open("datafile.txt", "r")

  image = Image.open(file)

  #Actual width / Desired width
  scaleFactor = image.size[0] / width
  height = math.floor(image.size[1] / scaleFactor)
  
  image.thumbnail((width, height), Image.BICUBIC)
  image.save("lastthing.png")

  emojis = []
  for line in datafile.readlines():
    s = line.split("|")
    em = s[0].split("~")[0]
    short = ".".join(s[0].split("~")[1].split(".")[0:-1])
    emojis.append({
      "emoji": em,
      "shortcode": short,
      "popular": list(map(int, s[1].split(","))),
      "average": list(map(int, s[2].split(","))),
      "percentPop": float(s[3]),
      "percentVis": float(s[4]),
    })

  output = []
  for h in range(height):
    row = []
    for w in range(width):
      pd = image.getpixel((w,h))
      bestemoji = None
      bestemojiscore = math.inf

      #If pixel data is not useable give default emoji
      if len(pd) > 3 and pd[3] < 255:
        row.append(DEFAULTEMOJI)
      else:
        for emoji in emojis:
          #Calc score based on 3 factors with different weighting
          ac = emoji["average"]
          ascore = sqrt(abs(ac[0] - pd[0])**2 + abs(ac[1] - pd[1])**2 + abs(ac[2] - pd[2])**2)
          pc = emoji["popular"]
          pscore = sqrt(abs(pc[0] - pd[0])**2 + abs(pc[1] - pd[1])**2 + abs(pc[2] - pd[2])**2)
          pv = emoji["percentVis"]
          pvscore = 255 * (1 - pv)

          score = (pscore*weight[0]) + (ascore*weight[1]) + (pvscore*weight[2])

          #Compare scores and reset variable
          if score < bestemojiscore:
            bestemojiscore = score
            bestemoji = emoji["emoji"]

        #Defaults to white square if there is no emoji
        if bestemoji:
          row.append(bestemoji)
        else:
          row.append(DEFAULTEMOJI)
    output.append(row)

  return output

if __name__ == '__main__':
  TOKEN = os.environ["DISCORD_TOKEN"]
  client.run(TOKEN)