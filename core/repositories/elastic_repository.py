from elasticsearch import Elasticsearch, NotFoundError
import logging

class ElasticRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        
        self.es = Elasticsearch(
            [f"{config['scheme']}://{config['host']}:{config['port']}"],
            basic_auth=(config['user'], config['password']),
            timeout=60
        )
        
    def save_scrap(self, scrap):
            try:
                response = self.es.index(index="scrapes", id=scrap.hash, document={
                    "source": scrap.source,
                    "content": scrap.content,
                    "attachments": scrap.attachments,
                    "timestamp": scrap.timestamp,
                    "filename": scrap.filename
                })
                self.logger.info(f"Scrap {scrap.hash} indexed in Elasticsearch with response: {response}.")
            except NotFoundError as e:
                self.logger.error(f"Index not found. Please create the index before indexing documents.")
                raise e
            except Exception as e:
                self.logger.error(f"Failed to index scrap {scrap.hash}: {e}")
                raise e
