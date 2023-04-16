"""
Chan Bot
Created by chan#2747 on Discord
3/9/23
"""



import os
import nextcord
import requests
import json
import datetime
import random
import time
import logging
import openai
import asyncio
from dotenv import load_dotenv
from nextcord.ext import commands
from nextcord import Interaction
from PIL import Image


load_dotenv()

# configure logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

intents = nextcord.Intents().all()
intents.members = True

openai.api_key = os.environ["OPENAI_API_KEY"]

bot = commands.Bot(intents=nextcord.Intents.all(), case_insensitive=True)
bot.last_compliment = {}

COMPLIMENT_COOLDOWN = 3600  # 1 hour in seconds
COMPLIMENTS = [
    "You are amazing!",
    "You're doing great, keep going :)",
    "You make this community a better place!",
    "You always make my day brighter!",
    "You are a blessing to those around you!",
]

async def register_slash_commands():
    # Replace this with your bot's application ID
    application_id = '1097236024670826597'
    url = f"https://discord.com/api/v10/applications/{application_id}/commands"

    headers = {
        "Authorization": f"Bot {os.environ['DISCORD_TOKEN']}",
        "Content-Type": "application/json",
    }

    slash_commands = [
    {
        "name": "gpt",
        "description": "Interact with GPT-3.5",
        "options": [
            {
                "name": "prompt",
                "description": "The prompt for GPT-3.5",
                "type": 3,
                "required": True,
            }
        ],
    },
    {
        "name": "bonk",
        "description": "Bonk a member",
        "options": [
            {
                "name": "member",
                "description": "The member to bonk",
                "type": 6,
                "required": True,
            }
        ],
    },
    {
        "name": "compliment",
        "description": "Compliment a member",
        "options": [
            {
                "name": "message",
                "description": "An optional message to include in the compliment",
                "type": 3,
                "required": False,
            }
        ],
    },
    {
        "name": "joke",
        "description": "Get a random joke",
        "options": [],
    },
    {
        "name": "history",
        "description": "Get a random fact from history",
        "options": [{"description": "Get a random fact from history"}],
    },
    {
        "name": "astronomy",
        "description": "Get an astronomy picture of the day",
        "options": [
            {
                "name": "date",
                "description": "The date to get the picture for in the format YYYY-MM-DD",
                "type": 3,
                "required": False,
            }
        ],
    },
    {
        "name": "pet",
        "description": "Get a picture of a pet",
        "options": [{"description": "Get a picture of a pet"}],
    },
    {
        "name": "doom",
        "description": "Get a random MF DOOM gif",
        "options": [{"description": "Get a random MF DOOM gif"}],
    },
]

    for command in slash_commands:
        response = requests.post(url, headers=headers, json=command)
        print(f"Registered command {command['name']}: {response.status_code}")

@bot.event
async def on_ready():
    logging.info('Bot is ready')
    print('Bot is ready')
    await register_slash_commands()

@bot.slash_command(name="gpt")
async def gpt_command(interaction: Interaction, *, prompt: str):
        logging.info(f"{interaction.user} used the /gpt command")
        await interaction.response.defer()

        response = await get_gpt_response(prompt)

        await asyncio.sleep(5)
        
        await interaction.followup.send(f"User: {prompt}\nGPT 3.5: {response}")

async def get_gpt_response(prompt):
    api_key = os.environ["OPENAI_API_KEY"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 350
    }
    url = "https://api.openai.com/v1/chat/completions"
    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()

    if "choices" in response_json and len(response_json["choices"]) > 0 and "message" in response_json["choices"][0]:
        return response_json["choices"][0]["message"]["content"]
    else:
        return "Error: Unable to retrieve chat response from the API."

@bot.slash_command(name='bonk')
async def bonk_command(interaction: Interaction, member: nextcord.Member):
    logging.info(f"{interaction.user} used the /bonk command")
    # Send a message in the channel to indicate who was bonked
    await interaction.response.send_message(f'{member.mention}, you have been bonked by {interaction.user.mention}!', file=nextcord.File('./bonk-doge.gif'))

@bot.slash_command(name='compliment')
async def compliment_command(interaction: Interaction, *, message: str=None):
    logging.info(f"{interaction.user} used the /compliment command")
    last_used = bot.last_compliment.get(interaction.user.id, 0)
    current_time = time.time()

    if current_time - last_used < COMPLIMENT_COOLDOWN:
        time_left = COMPLIMENT_COOLDOWN - int(current_time - last_used)
        await interaction.response.send_message(f"Sorry, you can only use this command once every hour. Try again in {time_left // 60} minutes.")
        return

    members = interaction.guild.members
    # Filter out bots and the command user
    members = [member for member in members if not member.bot and member != interaction.user]
    if len(members) == 0:
        await interaction.response.send_message("Sorry, I couldn't find any users to compliment!")
        return
    # Pick a random user from the list of members
    target_user = random.choice(members)
    compliment = f"{target_user.mention}, {message or random.choice(COMPLIMENTS)}"
    await interaction.response.send_message(compliment)

    bot.last_compliment[interaction.user.id] = current_time

@bot.slash_command(name='joke')
async def joke_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /joke command")
    joke = get_joke()
    await interaction.response.send_message(joke)

@bot.slash_command(name='history')
async def history_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /history command")
    # Get the current date and format it as 'month/day'
    now = datetime.datetime.now()
    today = now.strftime("%m/%d")

    # Fetch a random fact for the current day
    url = f"http://numbersapi.com/{today}/date"
    response = requests.get(url)
    
    # Send the fact to the channel
    if response.ok:
        fact = response.text
        await interaction.response.send_message(f"On this day in history: {fact}")
    else:
        await interaction.response.send_message("Sorry, I couldn't fetch a fact for today.")

@bot.slash_command(name='astronomy')
async def astronomy_command(interaction: Interaction, date: str=None):
    logging.info(f"{interaction.user} used the /astronomy command")

    if date:
        # If date is provided as an argument, use it
        formatted_date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
    else:
        # If date is not provided, get today's date
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")

    # Make a request to the Astronomy API with the formatted date
    url = f"https://api.nasa.gov/planetary/apod?api_key={os.environ['NASA_API_KEY']}&date={formatted_date}"
    response = requests.request("GET", url)
    data = json.loads(response.text)

    # Send the image and explanation to the channel
    await interaction.response.send_message(data['url'])
    followup = interaction.followup
    await followup.send(content=data['explanation'])

@bot.slash_command(name='pet')
async def pet_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /pet command")
    # Define the path to the directory containing Winston/Hazel pictures
    pet_dir = './winston_pics'

    # Get a list of all files in the directory
    pics = os.listdir(pet_dir)

    # Choose a random picture from the list
    chosen_pic = random.choice(pics)

    # Compress the image if it is larger than 8MB
    file_size = os.path.getsize(os.path.join(pet_dir, chosen_pic))
    while file_size > 8000000:
        with Image.open(os.path.join(pet_dir, chosen_pic)) as im:
            im = im.convert('RGB')
            im = im.resize((int(im.width * 0.9), int(im.height * 0.9)), resample=Image.LANCZOS)
            im.save(os.path.join(pet_dir, chosen_pic), optimize=True, quality=85)
        file_size = os.path.getsize(os.path.join(pet_dir, chosen_pic))

    # Create a file object for the chosen picture
    with open(os.path.join(pet_dir, chosen_pic), 'rb') as f:
        pic_file = nextcord.File(f)

    # Send the picture to the channel
    await interaction.response.send_message(file=pic_file)


@bot.slash_command(name='doom')
async def doom_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /doom command")
    # Make a request to the Giphy API to get a random image of MF DOOM
    url = "https://api.giphy.com/v1/gifs/random"
    params = {
        "api_key": os.environ['GIPHY_API_KEY'],
        "tag": "MF DOOM"
    }
    response = requests.request("GET", url, params=params)
    data = json.loads(response.text)

    # Send the image to the channel
    await interaction.response.send_message(data['data']['images']['original']['url'])

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

