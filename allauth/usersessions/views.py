from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.usersessions import app_settings
from allauth.usersessions.forms import ManageUserSessionsForm
from allauth.usersessions.models import UserSession


@method_decorator(login_required, name="dispatch")
class ListUserSessionsView(FormView):
    template_name = (
        f"usersessions/usersession_list.{account_settings.TEMPLATE_EXTENSION}"
    )
    form_class = ManageUserSessionsForm
    success_url = reverse_lazy("usersessions_list")

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        sessions = sorted(
            UserSession.objects.purge_and_list(self.request.user),
            key=lambda s: s.created_at,
        )
        ret["sessions"] = sessions
        ret["session_count"] = len(sessions)
        ret["show_last_seen_at"] = app_settings.TRACK_ACTIVITY
        return ret

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["request"] = self.request
        return ret

    def form_valid(self, form):
        form.save(self.request)
        get_account_adapter().add_message(
            self.request,
            messages.INFO,
            "usersessions/messages/sessions_logged_out.txt",
        )
        return super().form_valid(form)


list_usersessions = ListUserSessionsView.as_view()
