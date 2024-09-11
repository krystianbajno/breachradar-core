import psycopg2
import logging

from core.entities.scrap import Scrap

class PostgresRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.conn = self._connect()

    def _connect(self):
        try:
            return psycopg2.connect(**self.config)
        except psycopg2.Error as e:
            self.logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def get_connection(self):
        if self.conn is None or self.conn.closed:
            self.logger.info("Reconnecting to PostgreSQL...")
            self.conn = self._connect()
        return self.conn

    def save_scrap_reference(self, scrap, file_path, parent_scrape_id=None):
        query = """
        INSERT INTO scrapes (hash, source, filename, scrape_time, file_path, state, parent_scrape_id, timestamp) 
        VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (scrap.hash, scrap.source, scrap.filename, file_path, scrap.state, parent_scrape_id, scrap.timestamp))
            conn.commit()
            self.logger.info(f"Scrap {scrap.hash} saved successfully.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to save scrap {scrap.hash}: {e}")
            
    def get_latest_scrap(self, file_hash):
        query = """
        SELECT hash, file_path, parent_scrape_id, timestamp
        FROM scrapes 
        WHERE hash = %s 
        ORDER BY scrape_time DESC 
        LIMIT 1
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (file_hash,))
                result = cursor.fetchone()
                if result:
                    return Scrap(
                        hash=result[0], 
                        file_path=result[1], 
                        state='NEW', 
                        timestamp=result[3]
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to fetch latest scrap by hash {file_hash}: {e}")
            return None

    def reference_existing_scrap(self, scrap):
        """
        Update the reference of an existing scrap.
        """
        latest_scrap = self.get_latest_scrap(scrap.hash)
        if latest_scrap:
            parent_scrape_id = latest_scrap[0]
            query = "UPDATE scrapes SET parent_scrape_id = %s WHERE hash = %s"
            try:
                conn = self.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(query, (parent_scrape_id, scrap.hash))
                conn.commit()
                self.logger.info(f"Scrap {scrap.hash} updated with parent_scrape_id {parent_scrape_id}.")
            except Exception as e:
                if self.conn:
                    self.conn.rollback()
                self.logger.error(f"Failed to reference existing scrap {scrap.hash}: {e}")
        else:
            self.logger.warning(f"No existing scrap found to reference for hash {scrap.hash}")
            
    def get_scrap_by_hash(self, file_hash):
        query = "SELECT hash, source, file_path, state, timestamp FROM scrapes WHERE hash = %s"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (file_hash,))
                result = cursor.fetchone()
                if result:
                    return Scrap(
                        hash=result[0],
                        source=result[1],
                        file_path=result[2],
                        state=result[3],
                        timestamp=result[4]
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to fetch scrap by hash {file_hash}: {e}")
            return None

    def update_scrap_state(self, scrap_hash, state):
        query = "UPDATE scrapes SET state = %s WHERE hash = %s"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (state, scrap_hash))
            conn.commit()
            self.logger.info(f"Scrap {scrap_hash} updated to state {state}.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to update scrap {scrap_hash}: {e}")

    def get_unprocessed_scraps(self):
        query = "SELECT hash, file_path, source, timestamp FROM scrapes WHERE state != 'PROCESSED'"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                scraps = cursor.fetchall()
                return [
                    Scrap(
                        hash=row[0], 
                        file_path=row[1], 
                        source=row[2], 
                        timestamp=row[3]
                    ) 
                    for row in scraps
                ]
        except Exception as e:
            self.logger.error(f"Failed to fetch unprocessed scraps: {e}")
            return []

    def get_credential_regexes(self):
        query = "SELECT pattern FROM credential_patterns"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                patterns = [row[0] for row in cursor.fetchall()]
                return patterns
        except Exception as e:
            self.logger.error(f"Failed to fetch credential regexes: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            self.logger.info("Postgres connection closed.")
