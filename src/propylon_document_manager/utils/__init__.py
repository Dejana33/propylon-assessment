from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response
    return Response(
        {"detail": "An unexpected error occurred. Please contact support if the problem persists."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
