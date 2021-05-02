
import matplotlib.pyplot as plt, discord, os, re, sys
sys.path.append('../')

from nlp import scraper
from dotenv import load_dotenv
from googlesearch import search
from inspect import signature
from summarizer import Summarizer
from typing import Iterable
from wordcloud import WordCloud, STOPWORDS

bot = discord.Client()
send_raw_cmds = set()  # cmds that will be printed out directly in chat rather than a text file upload

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = 'powersearch-assistant'

print(TOKEN)
print(GUILD)
scraped_content = str()
links = list()

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
        msg_split = msg[1:].strip().split('`')
        url = msg_split[1]
        cmd_list = msg_split[2].strip().split(' ') if len(msg_split[2]) > 2 else list()

        if __debug__:
            await message.channel.send(content=str(url))

        # single url
        if re.search(pattern='(https?:\/\/)?[a-z].*\.[a-z]+', string=url):
            await message.channel.send(content='Single URL')
            if not url.startswith('http'):
                url = 'http://' + url

        # multiple key words
        elif re.search(pattern='(\s*\w+)(\s\w+)*\s*', string=url):
            await message.channel.send(content='Multiple key words')
            url = url.strip().split(' ')

        elif url == 'help':
            await message.channel.send(content='help')

        else:
            await message.channel.send(content='Incorrect syntax! Run !\`help\`')

        if __debug__:
            await message.channel.send(content=str(url))
            await message.channel.send(content=str(msg_split))
            await message.channel.send(content=str(cmd_list))

        if type(url) == list:
            await search_keywords_cmd(message=message, kws=url)

        for idx in range(1, len(cmd_list)):
            curr = cmd_list[idx]
            if curr == 'raw':
                send_raw_cmds.add(cmd_list[idx - 1])

        if __debug__:
            await message.channel.send(content='Before executing commands')

        if 'scrape' in cmd_list or type(url) == list:
            await scrape_cmd(message=message, url=url)
        if 'entities' in cmd_list:
            await entities_cmd(message=message, url=url)
        if 'summarize' in cmd_list:
            await summarize_cmd(message=message, url=url)
        if 'sentiment' in cmd_list:
            await sentiment_cmd(message=message, url=url)
        if 'topics' in cmd_list:
            await topics_cmd(message=message, url=url)

        scraped_content = str()
        links.clear()
        send_raw_cmds.clear()

        # sending final report from top links
        if type(url) == list:
            await message.channel.send(file=discord.File(fp='keyword_search.txt'))

def searchResults(query):
    global links
    links = search(term=query, num_results=5, lang='en')
    for link in links:
        print(link)
    return links

async def search_keywords_cmd(message: discord.Message, kws: Iterable[str]):
    """[summary]

    Args:
        message (discord.Message): [description]
        kws (Iterable[str]): [description]
    """
    query = ' + '.join(kws)
    if __debug__:
        await message.channel.send(content=query)

    links = searchResults(query=query)
    for link in links:
        await message.channel.send(content=link)

async def scrape_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        url (str): [description]
    """
    global scraped_content
    global send_raw_cmds

    # handling keyword queries
    if type(url) == list:
        global links
        scraped_content = str()
        for link in links:
            scraped_content += scraper.scrape_important_words(url=link) + '\n\n'
        with open(file='keyword_search.txt', mode='w') as f:
            f.write("**Scraping top websites from Google**\n\n" + scraped_content + '\n\n')
            f.close()
        return

    scraped_content = scraper.scrape_important_words(url=url)
    await message.channel.send(content=f'**Scraping {url}...**')

    if 'scrape' in send_raw_cmds:
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
    global send_raw_cmds

    # scraping must be done first before any analytics commands
    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    # only display printout message for single urls
    if type(url) != list:
        await message.channel.send(content=f'**Fetching entity links for {url}...**')

    # entity recognition code
    response = scraper.sample_analyze_entities(text_content=scraped_content)
    wikiLIST = scraper.findAllWikiLinks(response=response)

    # holds each entity and wiki site
    entities_textblock = str()
    for wiki in wikiLIST:
        entities_textblock += wiki.split('/')[-1] + wiki + '\n'

    # handling keyword queries
    if type(url) == list:
        with open(file='keyword_search.txt', mode='a') as f:
            f.write("**Finding entities and fetching wiki links**\n\n" + entities_textblock + '\n\n')
            f.close()
        return

    if 'entities' in send_raw_cmds:
        for wiki in wikiLIST:
            await message.channel.send(content=wiki.split('/')[-1] + wiki + '\n')
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
    global send_raw_cmds

    # scraping must be done first before any analytics commands
    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    # only display printout message for single urls
    if type(url) != list:
        await message.channel.send(content=f'**Summarizing {url}...**')

    # summarization code
    model = Summarizer()
    result = model(scraped_content, ratio=0.25)
    full = ''.join(result)

    # handling keyword queries
    if type(url) == list:
        with open(file='keyword_search.txt', mode='a') as f:
            f.write("**Summarizing collected text from websites together**\n\n" + full + '\n\n')
            f.close()
        return

    if 'summarize' in send_raw_cmds:
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
    global scraped_content
    global send_raw_cmds

    # scraping must be done first before any analytics commands
    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    # only display printout message for single urls
    if type(url) != list:
        await message.channel.send(content=f'**Analyzing sentiment for {url}...**')

    # sentiment analysis code
    response_sentiment = scraper.sample_analyze_sentiment(text_content=scraped_content)
    score = response_sentiment.document_sentiment.score
    magnitude = response_sentiment.document_sentiment.magnitude
    emoticon = scraper.emojify(response=response_sentiment)
    sentiment_report = f'sentiment score: {score}\nsentiment magnitude: {magnitude}\n{emoticon}\n\n'

    # handling keyword queries
    if type(url) == list:
        with open(file='keyword_search.txt', mode='a') as f:
            f.write("**Analyzing overall sentiment of collected links**\n\n" + sentiment_report + '\n\n')
            f.close()
        return

    if 'sentiment' in send_raw_cmds:
        await message.channel.send(content=sentiment_report)
    else:
        with open(file='sentiment.txt', mode='w') as f:
            f.write(sentiment_report)
            f.close()
        await message.channel.send(file=discord.File(fp='sentiment.txt'))

async def topics_cmd(message: discord.Message, url: str):
    """[summary]

    Args:
        message (discord.Message): [description]
        url (str): [description]
    """
    global scraped_content

    # scraping must be done first before any analytics commands
    if len(scraped_content) == 0:
        await scrape_cmd(message=message, url=url)

    await message.channel.send(content=f'**Generating topics for {url}...**')
    await message.channel.send(content=f'**Length of scraped content: {len(scraped_content)}**')

    wc = WordCloud(background_color='black', width=800, height=600, min_words=10, stopwords=set(STOPWORDS)).generate(text=str(scraped_content))
    plt.figure()
    plt.imshow(X=wc, aspect='auto', interpolation='bilinear')
    plt.imsave(fname='wordcloud.png', arr=wc, dpi=300)
    with open(file='wordcloud.png', mode='rb') as wc_image:
        await message.channel.send(file=discord.File(wc_image))

bot.run(TOKEN)
