from django.core.management import call_command


def test_unset_multipleprimaryemails(db):
    # This command needs to be dropped, in favor of having a conditional
    # constraint.
    call_command("account_unsetmultipleprimaryemails")
