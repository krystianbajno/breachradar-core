from elasticsearch import Elasticsearch, NotFoundError
import logging

class ElasticRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)

        self.host = config['host']
        self.port = config['port']
        self.es = Elasticsearch(
            hosts=[f"{config['scheme']}://{self.host}:{self.port}"],
            timeout=60,
            verify_certs=False
        )

    def save_scrap_chunk(self, elastic_chunk):
        try:
            response = self.es.index(index="scrapes_chunks", document={
                "scrap_id": elastic_chunk.scrap_id,
                "chunk_number": elastic_chunk.chunk_number,
                "content": elastic_chunk.chunk_content
            })
            elastic_id = response['_id']
            self.logger.info(f"Elastic chunk {elastic_chunk.chunk_number} for scrap {elastic_chunk.scrap_id} indexed in Elasticsearch with ID {elastic_id}.")
            return elastic_id
        except NotFoundError as e:
            self.logger.error("Index not found. Please create the index before indexing documents.")
            raise e
        except Exception as e:
            self.logger.error(f"Failed to index elastic chunk {elastic_chunk.chunk_number} for scrap {elastic_chunk.scrap_id}: {e}")
            raise e
