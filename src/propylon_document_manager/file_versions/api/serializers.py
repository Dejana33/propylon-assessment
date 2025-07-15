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
        if hasattr(obj, 'file') and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            file_name = request.data.get('file_name')
            if not file_name:
                raise serializers.ValidationError({"file_name": "File name is required."})
            if len(file_name) > 255:
                raise serializers.ValidationError({"file_name": "File name must be at most 255 characters."})
            if '/' in file_name or '\\' in file_name:
                raise serializers.ValidationError({"file_name": "File name cannot contain '/' or '\\'."})
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                max_size = 10 * 1024 * 1024
                if uploaded_file.size > max_size:
                    raise serializers.ValidationError({"file": "File size must not exceed 10MB."})
        return data
