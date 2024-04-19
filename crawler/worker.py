from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                #Print unique pages found
                print(f'Unique pages found: {len(self.frontier.downloaded)}')

                print()
                #Print longest page
                print(f'Longest page: {self.frontier.max_words_url} with {self.frontier.max_words} words')

                print()

                #Print most common words
                word_counts = self.frontier.word_counts.items()
                items = sorted(word_counts, key=lambda x: (-x[1], x[0]))
                items = [item[0] for item in items]
                print(f'50 most common words across pages:{items[:50]}')

                print()
                #Print subdomains of ics.uci.edu
                print('Subdomains of ics.uci.edu:')
                self.frontier.subdomains.pop("https://www.ics.uci.edu", None)
                subdomain_items = self.frontier.subdomains.items()
                subdomain_items = sorted(subdomain_items)
                for key, item in subdomain_items:
                    print(f'{key}, {item}')
                
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.frontier)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
