from django.core.management.base import BaseCommand
from propylon_document_manager.file_versions.models.file_version import FileVersion
from propylon_document_manager.file_versions.models.user import User
from propylon_document_manager.file_versions.models.file import File

file_versions = [
    'bill_document',
    'amendment_document',
    'act_document',
    'statute_document',
]

class Command(BaseCommand):
    help = "Load test file fixtures"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='user1@example.com',
            help='Email of the user for whom fixture files are created.'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='user123',
            help='Password of the user for whom fixture files are created.'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_password(password)
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