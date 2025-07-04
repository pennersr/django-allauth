from django.http import HttpResponse

from allauth.account.decorators import verified_email_required


@verified_email_required
def check_verified_email(request):
    return HttpResponse("VERIFIED")
