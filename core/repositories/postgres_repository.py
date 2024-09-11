import psycopg2
import logging

class PostgresRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.conn = psycopg2.connect(**config)
        
    def save_scrap_reference(self, scrap, file_path):
        query = """
        INSERT INTO scrapes (hash, source, filename, scrape_time, file_path, state) 
        VALUES (%s, %s, %s, NOW(), %s, %s)
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (scrap.hash, scrap.source, scrap.filename, file_path, scrap.state))
            self.conn.commit()
            self.logger.info(f"Scrap {scrap.hash} saved successfully.")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Failed to save scrap {scrap.hash}: {e}")

    def get_scrap_by_filename(self, filename):
        query = "SELECT filename FROM scrapes WHERE filename = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (filename,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            self.logger.error(f"Failed to fetch scrap by filename {filename}: {e}")
            return None

    def close(self):
        self.conn.close()
        self.logger.info("Postgres connection closed.")
