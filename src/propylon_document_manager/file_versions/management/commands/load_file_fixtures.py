from django.core.management.base import BaseCommand
from propylon_document_manager.file_versions.models import FileVersion, User, File

file_versions = [
    'bill_document',
    'amendment_document',
    'act_document',
    'statute_document',
]

class Command(BaseCommand):
    help = "Load test file fixtures"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(email="user1@example.com")
        if created:
            user.set_password("user123")
            user.save()
        for file_name in file_versions:
            file_obj, _ = File.objects.get_or_create(name=file_name, user=user)
            FileVersion.objects.create(
                file_obj=file_obj,
                version_number=1,
                user=user,
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully created %s file versions' % len(file_versions))
        )