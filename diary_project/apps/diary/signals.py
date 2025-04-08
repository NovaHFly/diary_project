from pathlib import Path

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Note


@receiver(pre_delete, sender=Note)
def delete_connected_note_file(sender, instance, **kwargs):
    file_path = Path(instance.file_path)
    file_path.unlink(missing_ok=True)
    dir_path = file_path.parent
    try:
        while True:
            dir_path.rmdir()
            dir_path = dir_path.parent
    except OSError:
        pass
