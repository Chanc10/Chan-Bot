"""
Chan Bot
Created by chan#2747 on Discord
3/9/23
!Current functions: /joke /history /astronomy
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

    # Check if the date has been fetched before, if not fetch a new fact
    if today not in bot.facts:
        try:
            fact = get_history_fact(today)
            bot.facts.add(today)
        except:
            fact = "Sorry, I couldn't fetch a fact for today."
    else:
        fact = "Sorry, I've already shared a fact for today."

    # Send the fact to the channel
    await ctx.send(f"On this day in history: {fact}")

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
    # Define the path to the directory containing Winston pictures
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

# Function to fetch a random joke from the API
def get_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.request("GET", url)
    joke_json = json.loads(response.text)
    joke = f"{joke_json['setup']} {joke_json['punchline']}"
    return joke

# Function to fetch a random historical fact based on the given date
def get_history_fact(date):
    url = f"https://history.muffinlabs.com/date/{date}"
    response = requests.request("GET", url)
    data = json.loads(response.text)

    # Get a random event from the list of events for the given date
    events = data['data']['Events']
    fact = random.choice(events)['text']

    return fact

# Set up a set to store the facts that have been fetched
bot.facts = set()

bot.run(os.environ['DISCORD_TOKEN'])


"""
TODO: Auto completion, music functionality, reactions
!Look for info on adding AI functionality



"""