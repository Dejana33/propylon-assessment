from django.shortcuts import render

from rest_framework.mixins import (
    RetrieveModelMixin, ListModelMixin, CreateModelMixin,
    UpdateModelMixin, DestroyModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView

from propylon_document_manager.file_versions.models.file_version import FileVersion
from propylon_document_manager.file_versions.models.file import File
from .serializers import FileVersionSerializer
import hashlib

permission_classes = [IsAuthenticated]

class FileVersionViewSet(
    RetrieveModelMixin, ListModelMixin, CreateModelMixin,
    UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return FileVersion.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        file_name = self.request.data.get("file_name")
        file_obj, created = File.objects.get_or_create(
            name=file_name,
            user=self.request.user
        )
        latest_version = FileVersion.objects.filter(file_obj=file_obj).order_by("-version_number").first()
        next_version = 1 if not latest_version else latest_version.version_number + 1

        uploaded_file = self.request.FILES["file"]
        sha256 = hashlib.sha256()
        for chunk in uploaded_file.chunks():
            sha256.update(chunk)
        content_hash = sha256.hexdigest()

        serializer.save(
            user=self.request.user,
            file_obj=file_obj,
            version_number=next_version,
            content_hash=content_hash
        )

    @action(detail=True, methods=["get"])
    def share(self, request, id=None):
        file_version = self.get_object()
        if file_version.file:
            link = request.build_absolute_uri(file_version.file.url)
            return Response({"shareable_link": link})
        return Response({"shareable_link": None}, status=404)

    @action(detail=False, methods=["get"], url_path="by_hash/(?P<content_hash>[0-9a-fA-F]{64})")
    def by_hash(self, request, content_hash=None):
        try:
            file_version = FileVersion.objects.get(content_hash=content_hash, user=request.user)
        except FileVersion.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(file_version, context={"request": request})
        return Response(serializer.data)

class FileByPathView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_path):
        revision = request.query_params.get("revision")
        try:
            file_obj = File.objects.get(name=file_path, user=request.user)
        except File.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if revision is not None:
            try:
                revision = int(revision)
                file_version = file_obj.versions.order_by("version_number")[revision]
            except (IndexError, ValueError):
                return Response({"detail": "Revision not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            file_version = file_obj.versions.order_by("-version_number").first()

        serializer = FileVersionSerializer(file_version, context={"request": request})
        return Response(serializer.data)

