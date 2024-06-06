from django.core.validators import RegexValidator


BattletagUsernameValidator = RegexValidator(r"^[\w.]+#\d+$")
