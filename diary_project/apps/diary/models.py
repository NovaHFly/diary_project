from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

DATA_PATH: Path = settings.DATA_PATH

User = get_user_model()


class Tag(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.SlugField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['author', 'name']
        constraints = [
            models.UniqueConstraint(
                name='Unique tag name for author',
                fields=['author', 'name'],
            ),
        ]


class Note(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    file_path = models.FilePathField(path=str(DATA_PATH))

    tags = models.ManyToManyField(Tag)

    @property
    def text(self) -> str:
        return Path(self.file_path).read_text()

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='Unique note creation time for author',
                fields=['author', 'created_at'],
            ),
            models.UniqueConstraint(
                name='Unique note title for author',
                fields=['author', 'title'],
            ),
        ]
