import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    print(soup.get_text())

    link_tags = soup.find_all('a')

    link_urls = [link.get('href') for link in link_tags]
    print(link_urls)

    # Extract the URLs from the anchor tags
    link_urls = []
    for link in link_tags:
        link = link.get('href')
        if link[0:2] == '//' and valid_domain(url):
            link_urls.append(link)
        elif link[0] == '/':
            link_urls.append(url + link)
        elif link[0:6] == 'https:' and valid_domain(url):
            link_urls.append(link)
    
    print(link_urls)

    return list()

    #TO DO:
    #PARSE LINKS CORRECTLY



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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

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
    
