import re
from urllib.parse import urlparse, urljoin, urlunparse
from urllib import robotparser
from bs4 import BeautifulSoup
from hashlib import sha256

def scraper(url, resp, frontier):
    return extract_next_links(url, resp, frontier)

def extract_next_links(url, resp, frontier):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


    #Add url to total set of extracted urls
    frontier.downloaded.add(url)

    #Return empty list if error
    if resp.status != 200:
        return list()
    
    #Parse html content
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    
    #Check meta robots tag
    robots_meta_tag = soup.find("meta", {"name": "robots"})
    if robots_meta_tag:
        #Extract the content attribute value
        content = robots_meta_tag.get("content").split(',')
        if "nofollow" in content:
            return list()

    text_content = soup.get_text()

    #Handle duplicate content
    content_hash = sha256(text_content.encode()).hexdigest()
    if content_hash in frontier.fingerprints:
        return list()
    frontier.fingerprints.add(content_hash)

    #Check content to html ration to see if page has high textual content
    text_content_len = len(text_content)
    html_content_len = len(resp.raw_response.content)

    ratio =  text_content_len / html_content_len
    if html_content_len == 0 or ratio < .06:
        return list()

    #Tokenize content and keep track of max words in frontier
    tokens = tokenize(text_content)
    if len(tokens) > frontier.max_words:
        frontier.max_words = len(tokens)
        frontier.max_words_url = url
    
    #Update word count for all pages
    token_freq = computeWordFrequencies(tokens)
    frontier.word_counts.update(token_freq)

    #Get all <a hrefs>s
    link_tags = soup.find_all('a', href=True)

    #Extract the URLs from the anchor tags and reformat
    link_urls = []
    for link in link_tags:
        link = link.get('href')
        if not link or link[0] == '#':
            pass
        elif link.startswith('//'):
            link = 'https:' + link
        elif link.startswith('/'):
            link = urljoin(url, link)
        #Remove query and fragment from link to avoid repetitive information
        link = urlunparse(urlparse(link)._replace(fragment='',query=''))
        #Add url to link list if it is valid and can be crawled
        if is_valid(link) and not urls_differ_by_at_most_two_chars(url, link) and not has_too_many_slashes(link, 4):
            link_urls.append(link)

    return link_urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|bib"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and valid_domain(url)

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def valid_domain(url):
    valid_domains = {'ics.uci.edu',
                    'cs.uci.edu',
                    'informatics.uci.edu',
                    'stat.uci.edu'}

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split('.')  
    if len(domain) < 3:
        return False
    #Get the last three parts of the domain
    domain = '.'.join(domain[-3:])
    return domain in valid_domains


def is_root_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path in ('', '/')

def urls_differ_by_at_most_two_chars(url1, url2):
    if len(url1) != len(url2):
        return False

    #Count the number of differing characters
    differing_chars = 0
    for char1, char2 in zip(url1, url2):
        if char1 != char2:
            differing_chars += 1
            # If the number of differing characters exceeds 2, return False immediately
            if differing_chars > 2:
                return False

    return True

def has_too_many_slashes(url, threshold):
    slash_count = url.count('/')
    return slash_count > threshold

def tokenize(text_content) -> list["Token"]:
    """
    Tokenize the text file at the given path and return a list of tokens
    """
    tokens = []
   
    #Build token and process token when encounter non alphanum char
    token = ""
    for char in text_content:
        char = char.lower()
        if (ord(char)>=97 and ord(char)<=122) or (ord(char)>=48 and ord(char)<=57) or ord(char)==39:
            token += char
        elif len(token)>=3:
            tokens.append(token)
            token = ""
        else:
            token = ""
    if token:
        tokens.append(token)

    return tokens

def computeWordFrequencies(tokens : list["Token"]) -> dict["Token", int]:
    """
    Compute the frequency of each word in the given list of tokens
    """
    freq = {}

    # Count the frequency of each token
    for token in tokens:
        if not token in stopwords:
            freq[token] = 1 + freq.get(token, 0)

    return freq

stopwords = {"a","about","above","after","again","against","all","am","an","and","any","are",
"aren't","as","at","be","because","been","before","being","below","between",
"both","but","by","can't","cannot","could","couldn't","did","didn't","do","does",
"doesn't","doing","don't","down","during","each","few","for","from","further","had",
"hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her",
"here","here's","hers","herself","him","his","how","how's","i","i'd","i'll","i'm",
"i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more",
"most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or",
"other","ought","our","ours"}