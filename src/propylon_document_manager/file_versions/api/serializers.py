from rest_framework import serializers

from propylon_document_manager.file_versions.models.file_version import FileVersion
from propylon_document_manager.file_versions.models.file import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name"]

class FileVersionSerializer(serializers.ModelSerializer):
    shareable_link = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)
    file_obj = FileSerializer(read_only=True)
    version_number = serializers.IntegerField(read_only=True)
    content_hash = serializers.CharField(read_only=True)

    class Meta:
        model = FileVersion
        fields = ["id", "file_obj", "version_number", "file", "shareable_link", "user", "content_hash"]

    def get_shareable_link(self, obj):
        request = self.context.get("request")
        if obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None
