from django_filters import CharFilter, FilterSet, ModelMultipleChoiceFilter

from diary.models import Note, Tag


class UserTagFilter(ModelMultipleChoiceFilter):
    def get_queryset(self, request):
        return Tag.objects.filter(author=request.user)


class NotesFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains')
    tags = UserTagFilter(
        field_name='tags__name',
        to_field_name='name',
    )

    class Meta:
        model = Note
        fields = [
            'title',
            'tags',
        ]


class TagsFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Tag
        fields = ['name']
