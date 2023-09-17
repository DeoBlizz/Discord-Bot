import os
import discord
import re

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?',intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hello(ctx):
    user = ctx.author
    await ctx.send(f'Hello {user.mention}!')

@bot.command()
async def calculate(ctx, *, expression):
    try:
        clean_expression = re.sub(r'[^\d+\-*/().]', '', expression)
        result = eval(clean_expression)
        await ctx.send(f'Result: {result}')
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')

bot.run(os.getenv('TOKEN'))