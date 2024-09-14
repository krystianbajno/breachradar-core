from elasticsearch import Elasticsearch, NotFoundError
import logging

class ElasticRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)

        self.es = Elasticsearch(
            hosts=[f"{config['scheme']}://{config['host']}:{config['port']}"],
            timeout=60,
            verify_certs=False
        )

    def save_scrap(self, scrap):
        try:
            response = self.es.index(index="scrapes", document={
                "source": scrap.source,
                "content": scrap.content, 
                "attachments": scrap.attachments,
                "timestamp": scrap.timestamp,
                "filename": scrap.filename
            })
            elastic_id = response['_id']
            self.logger.info(f"Scrap {scrap.hash} indexed in Elasticsearch with ID {elastic_id}.")
            return elastic_id
        except NotFoundError as e:
            self.logger.error("Index not found. Please create the index before indexing documents.")
            raise e
        except Exception as e:
            self.logger.error(f"Failed to index scrap {scrap.hash}: {e}")
            raise e
