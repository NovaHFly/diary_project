from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['author', 'name']


class Note(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    file_path = models.CharField(max_length=100)

    tags = models.ManyToManyField(Tag)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-created_at']
