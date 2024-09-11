import os

class MigrationServiceProvider:
    def __init__(self, app, migrations_dir='core/migrations'):
        self.app = app
        self.migrations_dir = migrations_dir

    def register(self):
        self.app.bind('MigrationService', lambda: self)

    def boot(self):
        pass

    def run_migrations_if_needed(self):
        postgres_repo = self.app.make('PostgresRepository')
        connection = postgres_repo.get_connection()

        try:
            self._ensure_migrations_table(connection)
            applied_migrations = self._get_applied_migrations(connection)
            migration_files = self._get_migration_files()

            for migration_file in migration_files:
                if migration_file not in applied_migrations:
                    self._apply_migration(connection, migration_file)
        finally:
            connection.close()

    def _ensure_migrations_table(self, connection):
        """Ensure the migrations table exists to track applied migrations."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            migration_filename VARCHAR UNIQUE,
            applied_at TIMESTAMP DEFAULT NOW()
        );
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute(create_table_sql)
                connection.commit()
            except Exception as e:
                connection.rollback()
                print(f"Error ensuring migrations table exists: {e}")

    def _get_applied_migrations(self, connection):
        """Fetch the list of already applied migrations from the migrations table."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT migration_filename FROM migrations;")
                applied_migrations = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching applied migrations: {e}")
            applied_migrations = []
        return applied_migrations

    def _get_migration_files(self):
        """Retrieve the list of migration files from the migrations directory."""
        migration_files = sorted(f for f in os.listdir(self.migrations_dir) if f.endswith('.sql'))
        return migration_files

    def _apply_migration(self, connection, migration_file):
        """Apply a single migration file within its own transaction."""
        migration_path = os.path.join(self.migrations_dir, migration_file)
        print(f"Applying migration: {migration_file}")

        with open(migration_path, 'r') as file:
            migration_sql = file.read()

        try:
            with connection.cursor() as cursor:
                cursor.execute(migration_sql)
                cursor.execute(
                    "INSERT INTO migrations (migration_filename) VALUES (%s);",
                    (migration_file,)
                )
                connection.commit()
            print(f"Migration {migration_file} applied successfully.")
        except Exception as e:
            connection.rollback()
            print(f"Error applying migration {migration_file}: {e}")
