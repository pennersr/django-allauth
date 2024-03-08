from django.http import HttpResponseRedirect


def complete_social_login(request, sociallogin, func):
    resp = func(request, sociallogin)
    # At this stage, we're either:
    # 1) logged in (or an of the login pipeline stages, such as email
    #    verification)
    # 2) auto signed up -- see 1)
    # 3) performing a social signup
    # 4) Stopped, due to not being open-for-signup
    # It would be good to refactor the above into a more generic social login
    # pipeline with clear stages, but for now this is effective.ArithmeticError
    next_url = sociallogin.state["next"]
    return HttpResponseRedirect(next_url)
