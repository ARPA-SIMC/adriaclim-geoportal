from django.core.management.base import BaseCommand
from Dataset.dataset_manager import getAllDatasets

class Command(BaseCommand):
    help = "Importa tutti i dataset iniziali"

    def handle(self, *args, **kwargs):
        try:
            getAllDatasets()
            self.stdout.write(self.style.SUCCESS('Dataset importati correttamente.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Errore durante l\'importazione: {e}'))
