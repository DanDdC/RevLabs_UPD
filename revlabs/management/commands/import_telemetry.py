from django.core.management.base import BaseCommand
from revlabs.telemetry_import import run_import


class Command(BaseCommand):
    help = 'Import telemetry laps from TelemetryIQ SQLite database'

    def add_arguments(self, parser):
        parser.add_argument('db_path', nargs='?', default=r'..\TelemetryIQ\telemetry.db')

    def handle(self, *args, **options):
        run_import(options['db_path'], print_func=self.stdout.write)
