import psycopg2
import logging
from core.entities.scrap import Scrap
from datetime import datetime

class PostgresRepository:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.conn = self._connect()

    def _connect(self):
        """Establish a new connection to the database."""
        try:
            return psycopg2.connect(**self.config)
        except psycopg2.Error as e:
            self.logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def get_connection(self):
        """Reconnect if the connection is closed or None."""
        if self.conn is None or self.conn.closed != 0:
            self.logger.info("Reconnecting to PostgreSQL...")
            self.conn = self._connect()
        return self.conn

    def save_scrap_reference(self, scrap, state='NEW'):
        """Save the scrap reference to the database."""
        processing_start_time = datetime.now() if state == 'PROCESSING' else None
        query = """
        INSERT INTO scrapes (hash, source, filename, scrape_time, file_path, state, timestamp, content, processing_start_time, occurrence_time, elastic_id)
        VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, NULL)
        RETURNING id
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    scrap.hash,
                    scrap.source,
                    scrap.filename,
                    scrap.file_path,
                    state,
                    scrap.timestamp,
                    psycopg2.Binary(scrap.content) if scrap.content else None,
                    processing_start_time,
                    scrap.occurrence_time
                ))
                scrap_id = cursor.fetchone()[0]
            conn.commit()
            self.logger.info(f"Scrap {scrap.hash} saved successfully with state '{state}' and id '{scrap_id}'.")
            return scrap_id
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to save scrap {scrap.hash}: {e}")
            return None

    def get_scrap_by_filename_and_hash(self, filename, file_hash):
        """Fetch a scrap by filename and hash."""
        query = """
        SELECT id, hash, source, filename, file_path, state, timestamp, content, occurrence_time, elastic_id
        FROM scrapes
        WHERE filename = %s AND hash = %s
        ORDER BY occurrence_time DESC
        LIMIT 1
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (filename, file_hash))
                result = cursor.fetchone()
                if result:
                    return Scrap(
                        id=result[0],
                        hash=result[1],
                        source=result[2],
                        filename=result[3],
                        file_path=result[4],
                        state=result[5],
                        timestamp=result[6],
                        content=result[7],
                        occurrence_time=result[8],
                        elastic_id=result[9]
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to fetch scrap by filename '{filename}' and hash '{file_hash}': {e}")
            return None

    def update_scrap_state(self, scrap_id, state):
        """Update the state of a scrap."""
        query = "UPDATE scrapes SET state = %s WHERE id = %s"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (state, scrap_id))
            conn.commit()
            self.logger.info(f"Scrap {scrap_id} updated to state '{state}'.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to update scrap {scrap_id}: {e}")

    def update_scrap_with_elastic_link(self, scrap_id, elastic_id):
        """Update scrap by adding the full Elasticsearch link and clearing content."""
        
        elastic_link = f"http://{self.config['host']}:{self.config['port']}/scrapes/_doc/{elastic_id}"

        query = """
        UPDATE scrapes
        SET elastic_id = %s, content = NULL
        WHERE id = %s
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (elastic_link, scrap_id))
            conn.commit()
            self.logger.info(f"Scrap {scrap_id} updated with elastic_id {elastic_link} and content cleared.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to update scrap {scrap_id} with elastic_link {elastic_link}: {e}")

    def clear_scrap_content(self, scrap_id):
        """Clear the content of a scrap after processing."""
        query = """
        UPDATE scrapes
        SET content = NULL
        WHERE id = %s
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (scrap_id,))
            conn.commit()
            self.logger.info(f"Content for scrap {scrap_id} cleared.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            self.logger.error(f"Failed to clear content for scrap {scrap_id}: {e}")

    def get_unprocessed_scraps(self, processing_timeout_minutes=30):
        """Fetch all unprocessed scraps or scraps stuck in 'PROCESSING' for too long."""
        query = """
        SELECT id, hash, source, filename, file_path, state, timestamp, content, occurrence_time
        FROM scrapes
        WHERE (state = 'NEW') OR
              (state = 'PROCESSING' AND processing_start_time < NOW() - INTERVAL '%s minutes')
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (processing_timeout_minutes,))
                scraps = cursor.fetchall()
                return [
                    Scrap(
                        id=row[0],
                        hash=row[1],
                        source=row[2],
                        filename=row[3],
                        file_path=row[4],
                        state=row[5],
                        timestamp=row[6],
                        content=row[7],
                        occurrence_time=row[8]
                    )
                    for row in scraps
                ]
        except Exception as e:
            self.logger.error(f"Failed to fetch unprocessed scraps: {e}")
            return []

    def get_scrap_by_id(self, scrap_id):
        """Fetch a scrap by ID."""
        query = """
        SELECT id, hash, source, filename, file_path, state, timestamp, content, occurrence_time, elastic_id
        FROM scrapes
        WHERE id = %s
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, (scrap_id,))
                result = cursor.fetchone()
                if result:
                    return Scrap(
                        id=result[0],
                        hash=result[1],
                        source=result[2],
                        filename=result[3],
                        file_path=result[4],
                        state=result[5],
                        timestamp=result[6],
                        content=result[7],
                        occurrence_time=result[8],
                        elastic_id=result[9]
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to fetch scrap by id {scrap_id}: {e}")
            return None

    def get_credential_patterns(self):
        """Fetch all credential patterns from the database."""
        query = "SELECT pattern FROM credential_patterns"
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                patterns = [row[0] for row in cursor.fetchall()]
            return patterns
        except Exception as e:
            self.logger.error(f"Failed to fetch credential patterns: {e}")
            return []

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.logger.info("Postgres connection closed.")
