from allauth.account.stages import LoginStageController
from allauth.account.utils import unstash_login


class AuthenticationState:
    def __init__(self, request):
        self.request = request

    @property
    def is_authenticated(self):
        return self.request.user.is_authenticated

    def get_stages(self):
        todo = []
        if self.is_authenticated:
            pass
        else:
            login = unstash_login(self.request, peek=True)
            if login:
                ctrl = LoginStageController(self.request, login)
                stages = ctrl.get_stages()
                for stage in stages:
                    if ctrl.is_handled(stage.key):
                        continue
                    todo.append(stage)
                    break
        return todo
