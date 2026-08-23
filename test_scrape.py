import sys
sys.path.append('backend')
from kshiraj.ingestion.crawler import GovtCrawler
from kshiraj.ingestion.models import CrawlPolicy

policy = CrawlPolicy()
policy.allowed_domains = ["standardsbis.gov.in"]
policy.crawl_delay_seconds = 1
policy.max_pages = 2

crawler = GovtCrawler()
res, docs = crawler.crawl_source(["https://standardsbis.gov.in"], policy)
print(res)
print(f"Extracted {len(docs)} documents.")
