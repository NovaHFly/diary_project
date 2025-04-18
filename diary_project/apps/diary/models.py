from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    Model,
    SlugField,
    TextField,
    UniqueConstraint,
)

from diary.constants import MAX_TITLE_LENGTH

User = get_user_model()


class Tag(Model):
    author = ForeignKey(User, on_delete=CASCADE)
    name = SlugField(max_length=MAX_TITLE_LENGTH)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['author', 'name']
        constraints = [
            UniqueConstraint(
                name='Unique tag name for author',
                fields=['author', 'name'],
            ),
        ]


class Note(Model):
    created_at = DateTimeField(auto_now_add=True)
    author = ForeignKey(User, on_delete=CASCADE)

    title = CharField(max_length=MAX_TITLE_LENGTH)
    text = TextField()

    tags = ManyToManyField(Tag, related_name='notes')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(
                name='Unique note title for author',
                fields=['author', 'title'],
            ),
        ]
