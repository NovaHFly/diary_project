import rest_framework.serializers as serializers

from diary.models import Note, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
        ]


class NoteSerializer(serializers.ModelSerializer):
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

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['tags'] = [tag['name'] for tag in repr['tags']]
        return repr

    def create(self, validated_data):
        tags = validated_data.pop('tags')

        validated_data['author'] = self.context['request'].user
        note = super().create(validated_data)

        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(**tag)
            note.tags.add(tag_obj)

        return note

    def update(self, instance: Note, validated_data):
        tags = validated_data.pop('tags')

        super().update(instance, validated_data)

        tags_list = [Tag.objects.get_or_create(**tag) for tag in tags]
        instance.tags.set(tags_list)

        return instance
