import re
from urllib.parse import urlparse, urljoin, urlunparse
from urllib import robotparser
from bs4 import BeautifulSoup

def scraper(url, resp):
    return extract_next_links(url, resp)

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    #Return empty list if error
    if resp.status != 200:
        return list()

    #Parse html content
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')

    #Get all <a hrefs>s
    link_tags = soup.find_all('a', href=True)

    # Extract the URLs from the anchor tags and reformat
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
        link = urlunparse(urlparse(link)._replace(query='',fragment=''))
        #Add url to link list if it is valid and can be crawled
        if is_valid(link):
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
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
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
    # Get the last three parts of the domain
    domain = '.'.join(domain[-3:])
    return domain in valid_domains


def is_root_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path in ('', '/')

