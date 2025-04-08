from pathlib import Path

import rest_framework.serializers as serializers

from diary.models import Note, Tag
from diary.util import write_to_random_file


class TagSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    def to_representation(self, instance: Tag) -> str:
        return instance.name

    def to_internal_value(self, data: str) -> dict:
        if not isinstance(data, str):
            raise serializers.ValidationError(
                f'Slug name expected, got: {repr(data)}'
            )
        return {'name': data, 'author': self.context['request'].user}

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'author',
        ]


class NoteSerializer(serializers.ModelSerializer):
    text = serializers.CharField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Note
        fields = [
            'id',
            'created_at',
            'title',
            'text',
            'tags',
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        text = validated_data.pop('text')

        file_path = str(write_to_random_file(text))
        validated_data['author'] = self.context['request'].user
        validated_data['file_path'] = file_path

        note = super().create(validated_data)

        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(**tag)
            note.tags.add(tag_obj)

        return note

    def update(self, instance: Note, validated_data):
        tags = validated_data.pop('tags')
        text = validated_data.pop('text')

        super().update(instance, validated_data)

        Path(instance.file_path).write_text(text)

        tags_list = [Tag.objects.get_or_create(**tag) for tag in tags]
        instance.tags.set(tags_list)

        return instance
