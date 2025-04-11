from django.contrib.auth import get_user_model
from django.db import models

from diary.constants import MAX_TITLE_LENGTH

User = get_user_model()


class Tag(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.SlugField(max_length=MAX_TITLE_LENGTH)

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

    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    text = models.TextField()

    tags = models.ManyToManyField(Tag)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='Unique note title for author',
                fields=['author', 'title'],
            ),
        ]
