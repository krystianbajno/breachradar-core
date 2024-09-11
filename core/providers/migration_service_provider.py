import os

class MigrationServiceProvider:
    def __init__(self, app, migration_file='migrations/20240830_all_migrations.sql'):
        self.app = app
        self.migration_file = migration_file

    def register(self):
        self.app.bind('MigrationService', lambda app: self)

    def run_migrations_if_needed(self):
        postgres_repo = self.app.make('PostgresRepository')
        connection = postgres_repo.get_connection()

        self._ensure_migrations_table(connection)

        applied_migrations = self._get_applied_migrations(connection)

        if os.path.basename(self.migration_file) not in applied_migrations:
            self._apply_migration(connection, self.migration_file)

        connection.close()

    def _ensure_migrations_table(self, connection):
        """Ensure the migrations table exists to track applied migrations."""
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    migration_filename VARCHAR UNIQUE,
                    applied_at TIMESTAMP DEFAULT NOW()
                );
            """)
            connection.commit()

    def _get_applied_migrations(self, connection):
        """Fetch the list of already applied migrations from the migrations table."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT migration_filename FROM migrations;")
            applied_migrations = [row[0] for row in cursor.fetchall()]
        return applied_migrations

    def _apply_migration(self, connection, migration_file):
        """Apply a single migration and record it in the migrations table."""
        print(f"Applying migration: {migration_file}")
        migration_path = os.path.join(os.getcwd(), migration_file)

        # Read the SQL content from the file
        with open(migration_path, 'r') as file:
            migration_sql = file.read()

        try:
            with connection.cursor() as cursor:
                # Execute the SQL from the migration file
                cursor.execute(migration_sql)
                # Record the migration in the migrations table
                cursor.execute(
                    "INSERT INTO migrations (migration_filename) VALUES (%s);",
                    (os.path.basename(migration_file),)
                )
                connection.commit()
            print(f"Migration {migration_file} applied successfully.")
        except Exception as e:
            connection.rollback()
            print(f"Error applying migration {migration_file}: {e}")
