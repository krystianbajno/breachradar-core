from elasticsearch import Elasticsearch
import logging

class ElasticRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        
        self.es = Elasticsearch([{
            'scheme': config['scheme'],
            'host': config['host'],
            'port': config['port']
        }])

    def save_scrap(self, scrap):
        try:
            self.es.index(index="scrapes", id=scrap.hash, document={
                "source": scrap.source,
                "content": scrap.content,
                "attachments": scrap.attachments,
                "timestamp": scrap.timestamp,
                "filename": scrap.filename
            })
            self.logger.info(f"Scrap {scrap.hash} indexed in Elasticsearch.")
        except Exception as e:
            self.logger.error(f"Failed to index scrap {scrap.hash}: {e}")
