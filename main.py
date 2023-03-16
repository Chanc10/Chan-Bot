"""
Chan Bot
Created by chan#2747 on Discord
3/9/23
!Current functions: /joke /history /astronomy /pet /doom
"""

import os
import discord
import requests
import json
import datetime
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

intents = discord.Intents().all()
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print('Bot is ready')

@bot.command(name='joke')
async def joke(ctx):
    joke = get_joke()
    await ctx.send(joke)

@bot.command(name='history')
async def history(ctx):
    # Get the current date and format it as 'month/day'
    now = datetime.datetime.now()
    today = now.strftime("%m/%d")

    # Fetch a random fact for the current day
    url = f"http://numbersapi.com/{today}/date"
    response = requests.get(url)
    
    # Send the fact to the channel
    if response.ok:
        fact = response.text
        await ctx.send(f"On this day in history: {fact}")
    else:
        await ctx.send("Sorry, I couldn't fetch a fact for today.")

@bot.command(name='astronomy')
async def astronomy(ctx):
    # Get today's date
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")

    # Make a request to the Astronomy API
    url = f"https://api.nasa.gov/planetary/apod?api_key={os.environ['NASA_API_KEY']}&date={date}"
    response = requests.request("GET", url)
    data = json.loads(response.text)

    # Send the image and explanation to the channel
    await ctx.send(data['url'])
    await ctx.send(data['explanation'])

@bot.command(name='pet')
async def pet(ctx):
    # Define the path to the directory containing Winston/Hazel pictures
    pet_dir = './winston_pics'

    # Get a list of all files in the directory
    pics = os.listdir(pet_dir)

    # Choose a random picture from the list
    chosen_pic = random.choice(pics)

    # Create a file object for the chosen picture
    with open(os.path.join(pet_dir, chosen_pic), 'rb') as f:
        pic_file = discord.File(f)

    # Send the picture to the channel
    await ctx.send(file=pic_file)

@bot.command(name='doom')
async def doom(ctx):
    # Make a request to the Giphy API to get a random image of MF DOOM
    url = "https://api.giphy.com/v1/gifs/random"
    params = {
        "api_key": os.environ['GIPHY_API_KEY'],
        "tag": "MF DOOM"
    }
    response = requests.request("GET", url, params=params)
    data = json.loads(response.text)

    # Send the image to the channel
    await ctx.send(data['data']['images']['original']['url'])

# Function to fetch a random joke from the API
def get_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.request("GET", url)
    joke_json = json.loads(response.text)
    joke = f"{joke_json['setup']} {joke_json['punchline']}"
    return joke

# Fetch a fact related to the specified date using the Numbers API
def get_history_fact(date):
    url = f"http://numbersapi.com/{date}/date"
    response = requests.get(url)
    if response.ok:
        return response.text
    else:
        return "Sorry, I couldn't fetch a fact for this date."

# Set up a set to store the facts that have been fetched
bot.facts = set()

bot.run(os.environ['DISCORD_TOKEN'])


"""
TODO: Auto completion, music functionality, reactions
!Look for info on adding AI functionality



"""