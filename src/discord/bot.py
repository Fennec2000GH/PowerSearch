
import discord
import os
import sys
sys.path.append('../')

from nlp import scraper
from dotenv import load_dotenv
from inspect import signature

bot = discord.Client()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = 'powersearch-assistant'

print(TOKEN)
print(GUILD)


@bot.event
async def on_ready():
    """[summary]
    """
    guilds_dict = dict([(guild.name, guild) for guild in bot.guilds])
    bot_guild = guilds_dict[GUILD]
    bot_channel = [channel for channel in bot_guild.channels if channel.name == CHANNEL][0]
    await bot_channel.send(content='PowerSearch Assistant present, how may I assist you?')
    
@bot.event
async def on_message(message: str):
    """[summary]

    Args:
        message (str): [description]
    """
    PREFIX = '!'
    msg = message.content
    # if message.author != bot:
    #     await message.channel.send(content=f'Echo: {msg}')
    
    # senses command
    if msg.startswith(PREFIX):
        message_list = msg[1:len(msg)].strip().split('\s+')
        print(f'message_list: {message_list}')

        url = message_list[0]
        scraped_content = scraper.scrape_important_words(url=url)
        
        await message.channel.send(content=f'Scraping {url}...')
        await message.channel.send(content=scraped_content)

bot.run(TOKEN)

