from django.conf import settings

def account(request):
    return {
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "support@example.com")
    }
