# PowerSearch Assistant quickstart
# Search single url
A search command for a single url takes the regex expression below:

!`(https?:\/\/)?[a-z].*\.[a-z]+`(\s+(scrape|entities|summarize|topics|raw))*

For an easier breakdown without regex, this may be more intuitive:

required:
!`[url]`

optional:
	scrape - webscrapes the url and captures only the text from important tags e.g. head, h1-h4, p
	entities - lists meaningful topic terms and links each associated Wikipedia article reference
	summarize - uses BERT summarizer to shorten scraped text to only the most important parts
	topics - displays a word cloud of most frequent and thus weighted terms
	raw - displays the output of preceding command as text directly in chat; default is save as a text file and upload
