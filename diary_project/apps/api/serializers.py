import rest_framework.serializers as serializers

from diary.models import Note, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
        ]

    def validate(self, attrs):
        if Tag.objects.filter(
            author=self.context['request'].user, name=attrs['name']
        ):
            raise serializers.ValidationError(
                f'Tag with name {attrs["name"]} exists!'
            )
        return attrs


class NoteSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.SlugField(),
        write_only=True,
    )

    class Meta:
        model = Note
        fields = [
            'id',
            'created_at',
            'title',
            'text',
            'tags',
        ]

    def validate(self, attrs):
        if Note.objects.filter(
            author=self.context['request'].user, title=attrs['title']
        ):
            raise serializers.ValidationError(
                f'Note with title {attrs["title"]} exists!'
            )
        return attrs

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['tags'] = [tag.name for tag in self.instance.tags.all()]
        return repr

    def create(self, validated_data):
        tags = validated_data.pop('tags')

        author = validated_data['author'] = self.context['request'].user
        note = super().create(validated_data)

        tags_list = [
            Tag.objects.get_or_create(name=tag, author=author)[0]
            for tag in tags
        ]
        note.tags.set(tags_list)

        return note

    def update(self, instance: Note, validated_data):
        tags = validated_data.pop('tags')

        super().update(instance, validated_data)

        author = self.context['request'].user
        tags_list = [
            Tag.objects.get_or_create(name=tag, author=author)[0]
            for tag in tags
        ]
        instance.tags.set(tags_list)

        return instance
