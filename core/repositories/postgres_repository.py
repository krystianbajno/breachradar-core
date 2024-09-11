import psycopg2
import logging

class PostgresRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.conn = self._connect()

    def _connect(self):
        """Establishes a new connection to the database."""
        try:
            return psycopg2.connect(**self.config)
        except psycopg2.Error as e:
            self.logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def get_connection(self):
        """Reconnects if the connection is closed or None."""
        if self.conn is None or self.conn.closed:
            self.logger.info("Reconnecting to PostgreSQL...")
            self.conn = self._connect()
        return self.conn

    def save_scrap_reference(self, scrap, file_path):
        query = """
        INSERT INTO scrapes (hash, source, filename, scrape_time, file_path, state) 
        VALUES (%s, %s, %s, NOW(), %s, %s)
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (scrap.hash, scrap.source, scrap.filename, file_path, scrap.state))
            conn.commit()
            self.logger.info(f"Scrap {scrap.hash} saved successfully.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to save scrap {scrap.hash}: {e}")

    def get_scrap_by_hash(self, file_hash):
        query = "SELECT hash, file_path FROM scrapes WHERE hash = %s"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (file_hash,))
                result = cursor.fetchone()
                return result
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

    def close(self):
        if self.conn:
            self.conn.close()
            self.logger.info("Postgres connection closed.")
