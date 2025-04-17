from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from diary.models import Note, Tag

from .filters import NotesFilter, TagsFilter
from .permissions import IsAuthor
from .serializers import NoteSerializer, TagSerializer


class NotesView(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotesFilter

    def get_queryset(self):
        return Note.objects.filter(author=self.request.user)


class TagsView(ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TagsFilter

    def get_queryset(self):
        return Tag.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
