from django.http import JsonResponse


class ErrorResponse(JsonResponse):
    def __init__(self, detail, status=400):
        super().__init__({"status": 400, "error": {"detail": detail}}, status=status)
