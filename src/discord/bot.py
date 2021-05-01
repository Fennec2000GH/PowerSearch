
import matplotlib.pyplot as plt, discord, os, sys
sys.path.append('../')

from nlp import scraper
from dotenv import load_dotenv
from inspect import signature
from summarizer import Summarizer
from wordcloud import WordCloud, STOPWORDS

bot = discord.Client()
send_raw = False  # whether to send raw text to the channel for each cmd; by deafult, a .txt file is sent

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = 'powersearch-assistant'

print(TOKEN)
print(GUILD)
scraped_content = str()

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
        url = msg[1:].strip().split(' ')[0].strip('`')
        if not url.startswith('http'):
            url = 'http://' + url

        cmd_list = [cmd for cmd in msg.strip().split(' ')[1:] if len(cmd) > 0]

        if __debug__:
            await message.channel.send(content=str(url))
            await message.channel.send(content=str(cmd_list))
            await message.channel.send(content=str(len(cmd_list)))

        if 'raw' in cmd_list:
            send_raw = True
        if 'scrape' in cmd_list:
            await scrape_cmd(message=message, url=url)
        if 'entities' in cmd_list:
            await entities_cmd(message=message, url=url)
        if 'summarize' in cmd_list:
            await summarize_cmd(message=message, url=url)
        if 'sentiment' in cmd_list:
            pass
        if 'topics' in cmd_list:
            await topics_cmd(message=message, url=url)
            
        scraped_content = str()
        send_raw = False

async def scrape_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        url (str): [description]
    """
    global scraped_content
    scraped_content = scraper.scrape_important_words(url=url)
    await message.channel.send(content=f'**Scraping {url}...**')

    if send_raw:
        # break scraped content into smaller chunks if more than 2000 char limit per Discord message
        if len(scraped_content) > 2000:
            scraped_contents_list = [chunk for chunk in scraped_content.split('\n') if len(chunk) > 0 and not str.isspace(chunk)]
            for chunk in scraped_contents_list:
                await message.channel.send(content=chunk)
        else:
            await message.channel.send(content=scraped_content)
    else:
        with open(file='scrape.txt', mode='w') as f:
            f.write(scraped_content)
            f.close()
        await message.channel.send(file=discord.File(fp='scrape.txt'))

async def entities_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        message (discord.Message): [description]
        url (str): [description]
    """
    global scraped_content
    await message.channel.send(content=f'**Fetching entity links for {url}...**')

    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    # entity recognition code
    response = scraper.sample_analyze_entities(text_content=scraped_content)
    wikiLIST = scraper.findAllWikiLinks(response=response)
    
    # holds each entity and wiki site
    entities_textblock = str()
    for wiki in wikiLIST:
        entities_textblock += wiki.split('/')[-1] + wiki + '\n'

    if send_raw:
        await message.channel.send(content=entities_textblock)
    else:
        with open(file='entities.txt', mode='w') as f:
            f.write(entities_textblock)
            f.close()
        await message.channel.send(file=discord.File(fp='entities.txt'))

async def summarize_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        message (discord.Message): [description]
        url (str): [description]
    """
    global scraped_content
    await message.channel.send(content=f'**Summarizing {url}...**')

    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    # summarization code
    model = Summarizer()
    result = model(model, ratio=0.25)
    full = ''.join(result)
    
    if send_raw:
        await message.channel.send(content=full)
    else:
        with open(file='summarize.txt', mode='w') as f:
            f.write(scraped_content)
            f.close()
        await message.channel.send(file=discord.File(fp='summarize.txt'))

async def sentiment_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        message (discord.Message): [description]
        url (str): [description]
    """
    await message.channel.send(content=f'**Analyzing sentiment for {url}...**')

    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    # sentiment analysis code
    
async def topics_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        message (discord.Message): [description]
        url (str): [description]
    """
    global scraped_content
    await message.channel.send(content=f'**Generating topics for {url}...**')

    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    await message.channel.send(content=f'length of scraped_content: {len(scraped_content)}')
    wc = WordCloud(background_color = 'white', max_words=20).generate(text=str(scraped_content))
    plt.figure()
    plt.imshow(X=wc, aspect='auto', interpolation='bilinear')
    plt.imsave(fname='wordcloud.png', arr=wc, dpi=300)
    with open(file='wordcloud.png', mode='rb') as wc_image:
        await message.channel.send(file=discord.File(wc_image))

bot.run(TOKEN)
