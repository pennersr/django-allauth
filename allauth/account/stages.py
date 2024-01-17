from allauth.account.adapter import get_adapter
from allauth.account.utils import resume_login, stash_login, unstash_login
from allauth.utils import import_callable


class LoginStage:
    key = None

    def __init__(self, controller, request, login):
        if not self.key:
            raise ValueError()
        self.controller = controller
        self.request = request
        self.login = login
        self.state = (
            self.login.state.setdefault("stages", {})
            .setdefault(self.key, {})
            .setdefault("data", {})
        )

    def handle(self):
        return None, True

    def exit(self):
        self.controller.set_handled(self.key)
        return resume_login(self.request, self.login)


class LoginStageController:
    def __init__(self, request, login):
        self.request = request
        self.login = login
        self.state = self.login.state.setdefault("stages", {})

    @classmethod
    def enter(cls, request, stage_key):
        login = unstash_login(request, peek=True)
        if not login:
            return None
        ctrl = LoginStageController(request, login)
        if ctrl.state.get("current") != stage_key:
            return None
        stages = ctrl.get_stages()
        for stage in stages:
            if stage.key == stage_key:
                return stage
        return None

    def set_current(self, stage_key):
        self.state["current"] = stage_key

    def is_handled(self, stage_key):
        return self.state.get(stage_key, {}).get("handled", False)

    def set_handled(self, stage_key):
        stage_state = self.state.setdefault(stage_key, {})
        stage_state["handled"] = True

    def get_stages(self):
        stages = []
        adapter = get_adapter(self.request)
        paths = adapter.get_login_stages()
        for path in paths:
            cls = import_callable(path)
            stage = cls(self, self.request, self.login)
            stages.append(stage)
        return stages

    def handle(self):
        stages = self.get_stages()
        for stage in stages:
            if self.is_handled(stage.key):
                continue
            self.set_current(stage.key)
            response, cont = stage.handle()
            if response:
                if cont:
                    stash_login(self.request, self.login)
                else:
                    unstash_login(self.request)
                return response
            else:
                assert cont
        unstash_login(self.request)
