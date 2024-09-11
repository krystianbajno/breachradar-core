import time
from core.app import App
from core.config.config import Config
from core.providers.app_service_provider import AppServiceProvider
from core.providers.app_entity_provider import AppEntityProvider
from core.providers.app_system_provider import AppSystemProvider
from core.providers.migration_service_provider import MigrationServiceProvider
from core.ecs.ecs_manager import ECSManager

def main():
    config = Config()
    app = App()

    app.bind('config', lambda: config)
    app.configuration = config
    
    app.register(AppServiceProvider)
    
    app.register(MigrationServiceProvider)
    app.make('MigrationService').run_migrations_if_needed()

    app.register(AppEntityProvider)
    app.register(AppSystemProvider)

    app.boot()

    ecs_manager = ECSManager(app)
    ecs_manager.run()

    app.run_systems(lambda x: time.sleep(config.get("system_tick", 1)))

if __name__ == "__main__":
    main()
