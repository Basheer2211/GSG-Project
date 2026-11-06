from pathlib import Path
from uuid import uuid4

from app.application.interfaces.file_storage import IFileStorage


class LocalFileStorage(IFileStorage):

    def __init__(self):
        self.storage_path = Path("storage/cvs")
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, extension: str) -> str:
        filename = f"{uuid4().hex}{extension}"
        file_path = self.storage_path / filename

        with open(file_path, "xb") as destination:
            destination.write(content)

        return str(file_path)