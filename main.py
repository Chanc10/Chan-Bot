"""
Chan Bot
Created by chan#2747 on Discord
3/9/23
"""



import os
import io
import nextcord
import requests
import json
import datetime
import random
import time
import logging
import openai
import asyncio
import yt_dlp
import random
import re
from dotenv import load_dotenv
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import File
from PIL import Image


load_dotenv()

# configure logging
logging.basicConfig(filename='bot.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

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
        "name": "art",
        "description": "AI generate art with DALL-E",
        "options": [
            {
                "name": "prompt",
                "description": "The prompt for DALL-E",
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
    {
        "name": "play",
        "description": "Play a song",
        "options": [{"description": "Play a song"}]
    },
    {
        "name": "pause",
        "description": "Pause the song",
        "options": [{"description": "Pause the song"}]
    },
    {
        "name": "resume",
        "description": "Resume the song",
        "options": [{"description": "Resume the song"}]
    },
    {
        "name": "skip",
        "description": "Skip the current song",
        "options": [{"description": "Skip the current song"}]
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
    
def get_audio_url(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['formats'][0]['url']

    return audio_url



'''
@bot.slash_command(name="geoguessr")
async def geoguessr(ctx: Interaction):
    """Starts a GeoGuessr mini-game"""
    # Send initial message
    await ctx.response.send_message("Welcome to GeoGuessr! Please enter a country or city to play with.")
    
    # Wait for user input
    country_or_city = None
    while country_or_city is None:
        try:
            country_or_city = await bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.user and m.channel == ctx.channel,
                timeout=60.0,
            )
            # Attempt to get location data from user input
            location_data = get_location_data(country_or_city.content)
            if location_data is None:
                await ctx.response.send_message("Sorry, I couldn't find any location data for that input. Please try again.")
                country_or_city = None
        except asyncio.TimeoutError:
            await ctx.response.send_message("Sorry, you took too long to respond. Please try again.")
            return
    
    # Get a random street view image for the location
    random_lat, random_lon = get_random_coordinates(location_data["bounds"])
    street_view_url = get_street_view_url(random_lat, random_lon)
    image_url = get_street_view_image_url(street_view_url)

    # Download the street view image
    image_data = requests.get(image_url).content
    with open("street_view.jpg", "wb") as f:
        f.write(image_data)

    # Send the image to the user and prompt them for their guess
    with open("street_view.jpg", "rb") as f:
        file = nextcord.File(f)
        await ctx.channel.send(file=file)
    await ctx.send("Where do you think this is? Please enter a country or city.")
    
    # Wait for user input
    guess = None
    while guess is None:
        try:
            guess = await bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60.0,
            )
        except asyncio.TimeoutError:
            await ctx.response.send_message("Sorry, you took too long to respond. The correct answer was: {0}.".format(location_data["name"]))
            return
    
    # Check the user's guess
    if check_guess(guess.content, location_data):
        await ctx.response.send_message("Congratulations! You guessed correctly!")
    else:
        await ctx.response.send_message("Sorry, that's not quite right. The correct answer was: {0}.".format(location_data["name"]))


# Helper functions for the GeoGuessr mini-game

def get_location_data(query: str) -> dict:
    """
    Gets location data for a given query (city or country)
    """
    response = requests.get(f"https://nominatim.openstreetmap.org/search?q={query}&format=json").json()
    if len(response) == 0:
        return None
    return {
        "name": response[0]["display_name"],
        "bounds": response[0]["boundingbox"]
    }

def get_random_coordinates(bounds: list) -> tuple:
    """
    Gets a random set of coordinates within a given bounding box
    """
    min_lat, max_lat, min_lon, max_lon = bounds
    random_lat = random.uniform(float(min_lat), float(max_lat))
    random_lon = random.uniform(float(min_lon), float(max_lon))
    return random_lat, random_lon

def get_street_view_url(lat: float, lon: float) -> str:
    """
    Gets the Google Maps street view URL for a given set of coordinates
    """
    return f"https://maps.googleapis.com/maps/api/streetview?size=640x640&location={lat},{lon}&key=AIzaSyC7l3Ddm2Lxol6lK8HT-r_Fmf_0SWx9mYg"

def get_street_view_image_url(url: str) -> str:
    """
    Downloads the street view image from the given URL
    """
    return url

def check_guess(guess: str, location_data: dict) -> bool:
    """
    Checks if the user's guess is correct by comparing it to the actual location data
    """
    # Remove extra whitespace and convert both strings to lowercase for comparison
    normalized_guess = guess.strip().lower()
    normalized_location_name = location_data["name"].strip().lower()

    # Check if the guess is in the location name (e.g. 'paris' in 'paris, france')
    if normalized_guess in normalized_location_name:
        return True

    # Check if the location name is in the guess (e.g. 'paris, france' in 'paris')
    if normalized_location_name in normalized_guess:
        return True

    # If neither of the above checks is true, the guess is incorrect
    return False

        #add this to slash_commands
    {
        "name": "geoguessr",
        "description": "Play a round of GeoGuessr",
        "options": [
            {
                "name": "query",
                "description": "The location to guess",
                "type": 3,
                "required": True,
            }
        ],
    }

'''
'''
@bot.slash_command(name="play")
async def play_command(interaction: nextcord.Interaction, url: str):
    voice_channel = interaction.user.voice.channel

    # Connect to the voice channel if not already connected
    if not interaction.guild.voice_client:
        await voice_channel.connect()

    # Get the audio URL using yt_dlp
    audio_url = get_audio_url(url)

    # Create an FFmpeg audio source
    ffmpeg_audio_source = nextcord.FFmpegPCMAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

    logging.info(f'Playing audio from URL: {audio_url}')
    # Play the audio in the voice channel
    interaction.guild.voice_client.play(ffmpeg_audio_source)

    # Send a message to the channel
    await interaction.response.send_message(f"Playing audio from: {url}")

@bot.slash_command(name='pause')
async def pause_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /pause command")
    voice_client = interaction.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("Paused.")
    else:
        await interaction.response.send_message("Nothing is playing.")

@bot.slash_command(name='resume')
async def resume_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /resume command")
    voice_client = interaction.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("Resumed.")
    else:
        await interaction.response.send_message("Nothing is paused.")

@bot.slash_command(name='skip')
async def skip_command(interaction: Interaction):
    logging.info(f"{interaction.user} used the /skip command")
    voice_client = interaction.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("Skipped.")
    else:
        await interaction.response.send_message("Nothing is playing.")
'''


dalle_api_key = os.environ["DALLE_API_KEY"]


@bot.slash_command(name="art")
async def art_command(interaction: Interaction, *, prompt: str):
    logging.info(f"{interaction.user} used the /art command")
    await interaction.response.defer()

    generated_image = await generate_dalle_image(prompt)

    await asyncio.sleep(5)

    if generated_image is not None and is_valid_url(generated_image):
        embed = nextcord.Embed()
        embed.set_image(url=generated_image)
        await interaction.followup.send(embed=embed)
    else:
        print(f"Invalid image URL: {generated_image}")
        await interaction.followup.send("Sorry, I could not generate an image from the provided description. Please try again.")



def is_valid_url(url: str) -> bool:
    url_regex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(url_regex.match(url))

async def generate_dalle_image(prompt: str):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = response["data"][0]["url"]
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

async def send_large_message(channel, message, chunk_size=2000):
    for i in range(0, len(message), chunk_size):
        await channel.send(message[i:i + chunk_size])


@bot.slash_command(name="gpt")
async def gpt_command(interaction: Interaction, *, prompt: str):
    logging.info(f"{interaction.user} used the /gpt command")
    await interaction.response.defer()

    response = await get_gpt_response(prompt)

    await asyncio.sleep(5)

    response_message = f"User: {prompt}\nGPT 3.5:\n{response}"
    await send_large_message(interaction.followup, response_message)

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
        "max_tokens": 500
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
    # Make a request to the Giphy API to get a list of images of MF DOOM
    url = "https://api.giphy.com/v1/gifs/search"  # Use the search endpoint
    params = {
        "api_key": os.environ['GIPHY_API_KEY'],
        "q": "MF DOOM",
        "limit": 25  # Limit the number of results to 25 (maximum allowed by the API)
    }
    response = requests.get(url, params=params)  # Use requests.get() for simplicity
    data = json.loads(response.text)

    # Randomly select an image from the results
    random_gif = random.choice(data['data'])

    # Send the image to the channel
    await interaction.response.send_message(random_gif['images']['original']['url'])

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

