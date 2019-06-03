from rest_framework import serializers
from projects.models import Project, Module, Technology, Requirement, Snapshot, ProjectFile
from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Project Tags"""

    class Meta:
        model = Tag
        fields = ('title',)


class RequirementSerializer(serializers.ModelSerializer):
    """Serializer for Project requirements"""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Requirement
        fields = ('id', 'name',)


class TechnologySerializer(serializers.ModelSerializer):
    """Serializer for Project technologies"""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Technology
        fields = ('id', 'name',)


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Project Modules"""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Module
        fields = ('id', 'name',)


class SnapshotSerializer(serializers.ModelSerializer):
    """Serializer for Project Snapshots"""

    class Meta:
        model = Snapshot
        fields = ('id', 'project', 'image',)
        read_only_fields = ('id',)


class ThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for Project Thumbnails"""

    class Meta:
        model = Project
        fields = ('id', 'image',)
        read_only_fields = ('id',)


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Project Video"""

    class Meta:
        model = Project
        fields = ('id', 'video',)
        read_only_fields = ('id',)


class FileSerializer(serializers.ModelSerializer):
    """Serializer for Project files"""

    slug = serializers.CharField(source='project.slug', read_only=True)

    class Meta:
        model = ProjectFile
        fields = ['id', 'project', 'file', 'slug']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project"""

    modules = ModuleSerializer(many=True)
    technologies = TechnologySerializer(many=True)
    requirements = RequirementSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'slug',
            'user',
            'title',
            'image',
            'description',
            'category',
            'price',
            'service_fees',
            'ratings',
            'modules',
            'technologies',
            'requirements',
            'tags',
            'link',
            'discount_rate',
            'on_sale'
            ]
        read_only_fields = ('image',)

    def create(self, validated_data):
        user = validated_data['user']
        modules = validated_data.pop('modules')
        technologies = validated_data.pop('technologies')
        requirements = validated_data.pop('requirements')
        tags = validated_data.pop('tags')
        project = Project.objects.create(**validated_data)
        if modules:
            for module in modules:
                Module.objects.create(**module, project=project)
        if technologies:
            for technology in technologies:
                Technology.objects.create(**technology, project=project)
        if requirements:
            for requirement in requirements:
                Requirement.objects.create(**requirement, project=project)
        if tags:
            for tag in tags:
                Tag.objects.create(**tag, project=project)

        return project

    def update(self, instance, validated_data):

        instance.title = validated_data.get('title', instance.title)
        instance.save()
        for key in validated_data.keys():
            if key in 'modules':
                modules = validated_data.pop('modules')
                return self.sub_details(modules, Module, instance)
            if key in 'technologies':
                technologies = validated_data.pop('technologies')
                return self.sub_details(technologies, Technology, instance)
            if key in 'requirements':
                requirements = validated_data.pop('requirements')
                return self.sub_details(requirements, Requirement, instance)
        return instance

    def sub_details(self, array, model, instance):
        keep_items = []
        for item in array:
            if "id" in item.keys():
                if model.objects.filter(id=item["id"]).exists():
                    m = model.objects.get(id=item["id"])
                    m.name = item.get('name', m.name)
                    m.save()
                    keep_items.append(m.id)
                else:
                    continue
            else:
                m = model.objects.create(**item, project=instance)
                keep_items.append(m.id)
        #
        # for module in Module.objects.all():
        #     print(module)
        #     if module["id"] not in keep_modules:
        #         module.delete()

        return instance


class ProjectCardSerializer(serializers.ModelSerializer):
    """Serializer for selected project cards attributes"""

    username = serializers.CharField(source='user.username')

    class Meta:
        model = Project
        fields = [
            'id',
            'slug',
            'image',
            'title',
            'username',
            'ratings',
            'price',
            'category',
            'discount_rate',
            'on_sale'
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for project complete attributes"""

    snapshots = SnapshotSerializer(many=True, read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    technologies = TechnologySerializer(many=True, read_only=True)
    requirements = RequirementSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    file = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        depth = 1

