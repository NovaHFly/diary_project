import secrets
from pathlib import Path

from django.conf import settings

DATA_PATH: Path = settings.DATA_PATH


def write_to_random_file(text: str) -> Path:
    file_path = (
        DATA_PATH
        / secrets.token_hex(16)
        / secrets.token_hex(16)
        / secrets.token_hex(16)
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text)
    return file_path.absolute()
