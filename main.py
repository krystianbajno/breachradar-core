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

    app.register(AppServiceProvider)
    app.register(AppEntityProvider)
    app.register(AppSystemProvider)
    app.register(MigrationServiceProvider)

    app.make(MigrationServiceProvider).run_migrations_if_needed()

    app.boot()

    ecs_manager = ECSManager(app)
    ecs_manager.run()

    app.run_systems(lambda entities: time.sleep(entities["settings"].get_component_by_id("system_tick")))

if __name__ == "__main__":
    main()
