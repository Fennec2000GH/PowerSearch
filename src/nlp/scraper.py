

from bs4 import BeautifulSoup, SoupStrainer
import requests

def scrape_important_words(url: str):
    """Soups HTML from given url.

    Args:
        url (str): Url to scrape web content from.
    """
    req = requests.get(url=url)
    bs = BeautifulSoup(markup=req.text)
    # print(bs)
    
    # tags to consider that may contain important words in website
    important_tags = list(['title', 'head', 'thead', 'h1', 'h2', 'h3', 'h4', 'p'])
    
    important_tags_text = [tag.text for tag in bs.find_all(name=important_tags)]
    important_tags_textblock = '\n'.join(important_tags_text)
    print(important_tags_textblock)
    return important_tags_textblock

if __name__ == '__main__':
    url = 'http://textblob.readthedocs.io/en/dev/quickstart.html#noun-phrase-extraction'
    scrape_important_words(url = url)
