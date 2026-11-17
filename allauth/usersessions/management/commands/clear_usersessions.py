from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError, CommandParser

from allauth.usersessions.internal.flows import sessions


class Command(BaseCommand):
    help = "Deletes expired user sessions."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--batch-size",
            default=sessions.DEFAULT_CLEAR_BATCH_SIZE,
            type=int,
            help="Maximum number of user sessions to delete per batch.",
        )

    def handle(self, *args, **options) -> None:
        batch_size = options["batch_size"]
        if batch_size <= 0:
            raise CommandError("--batch-size must be greater than zero.")
        count = sessions.clear_expired(batch_size=batch_size)
        self.stdout.write(f"{count} expired user session(s) deleted.")
