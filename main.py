import os
import discord
import re
import youtube_dl
import ffmpeg
import asyncio

from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?',intents=intents)
last_played_time = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hello(ctx):
    user = ctx.author
    await ctx.send(f'Hello {user.mention}!')

@bot.command()    
async def join(ctx):
    # Check if the author is in a voice channel
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # Check if the bot is already in a voice channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
    else:
        await ctx.send("User not in a voice chat")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("No longer in a voice channel")

@bot.command()
async def calculate(ctx, *, expression):
    try:
        clean_expression = re.sub(r'[^\d+\-*/().]', '', expression)
        result = eval(clean_expression)
        await ctx.send(f'Result: {result}')
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')

@bot.command()
async def play(ctx, url):
    global last_played_time
    # Check if the author is in a voice channel
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # Check if the bot is already in a voice channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice_client = ctx.voice_client
            if not voice_client.is_playing():
                voice_client.play(discord.FFmpegPCMAudio(url2))
                await ctx.send(f'Now playing: {info["title"]}')
                last_played_time = asyncio.get_event_loop().time()
            else:
                await ctx.send("I'm already playing a song!")
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

# A background task to check for inactivity and disconnect the bot
@tasks.loop(minutes=10)
async def check_activity():
    global last_played_time
    if last_played_time is not None:
        current_time = asyncio.get_event_loop().time()
        if current_time - last_played_time >= 600:
            for voice_client in bot.voice_clients:
                await voice_client.disconnect()
                last_played_time = None

# Start the background task
check_activity.start()

bot.run(os.getenv('TOKEN'))