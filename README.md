# PowerSearch Assistant Quickstart
-----------------------------------
![Python3](https://img.shields.io/badge/Language-Python3-yellow)
![JS/HTML/CSS](https://img.shields.io/badge/web-JS/HTML/CSS-orange)

![bot](https://img.shields.io/badge/discord-bot-indigo?style=for-the-badge&logo=appveyor)
![react](https://img.shields.io/badge/framework-react-seablue?style=for-the-badge&logo=appveyor)
![datastax astra - apache cassandra](https://img.shields.io/badge/database-Datastax%20Astra%20--%20Apache%20Cassandra-blueviolet?style=for-the-badge&logo=appveyor)

## Search single url
A search command for a single url takes the regex expression below:

!`(https?:\/\/)?[a-z].*\.[a-z]+`(\s+(scrape|entities|summarize|topics|raw))*

For an easier breakdown without regex, this may be more intuitive:

**required:**
!`[url]`

**optional:**<br>
	<br>scrape - webscrapes the url and captures only the text from important tags e.g. head, h1-h4, p
	-<br>entities - lists meaningful topic terms and links each associated Wikipedia article reference
	-<br>summarize - uses BERT summarizer to shorten scraped text to only the most important parts
	-<br>topics - displays a word cloud of most frequent and thus weighted terms
	-<br>raw - displays the output of preceding command as text directly in chat; default is save as a text file and upload

**Example:**
!`www.tesla.com` summarize entities topics

## Search multiple key words
Querying Google for keywords follows a slighltly different format:

**required:**
!`keyword1 keyword2 keyword3...`

**optional:**
    same commands as above, except "raw" since the output is very large and sent as a single text file

**Example:**
!`tom jerry cat mouse` entities
