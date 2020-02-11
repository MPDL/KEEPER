# encoding: utf-8
import logging

from django.utils import translation
from seahub.profile.models import Profile
from django.core.management.base import BaseCommand
import seaserv

from seahub.utils.mail import send_html_email_with_dj_template, MAIL_PRIORITY

# Get an instance of a logger
logger = logging.getLogger(__name__)

def get_user_language(username):
    return Profile.objects.get_user_language(username)

class Command(BaseCommand):
    help = 'Send Email notifications to users and admins on a keeper archiving action.'
    label = "notifications_notify_on_archiving"

    def add_arguments(self, parser):
        parser.add_argument('args_str', nargs=1, type=str)

    def handle(self, *args, **options):
        self.do_emails(options['args_str'][0])

    def do_emails(self, args_str):

        args = args_str.split('|', 5)

        if args[0] == 'ERROR':

            # notify admins
            db_users = seaserv.get_emailusers('DB', -1, -1)

            admins = []
            for user in db_users:
                if user.is_staff:
                    admins.append(user)
            for u in admins:
                send_html_email_with_dj_template(
                    u.email, dj_template='notifications/notify_admins_on_archiving_error.html',
                    context = {
                        'archive_id': args[2],
                        'error_msg': args[5],
                    },
                    subject="Error on keeper archiving, archive id: {}".format(args[2]),
                    priority=MAIL_PRIORITY.now
                )

            # notify owner
            cur_language = translation.get_language()

            user_language =  get_user_language(args[1])
            translation.activate(user_language)

            send_html_email_with_dj_template(
                args[1], dj_template='notifications/notify_user_on_archiving_error.html',
                context = {
                    'email': args[1],
                    'repo_id': args[3],
                    'repo_name': args[4],
                },
                subject="Error on keeper archiving, library id: {}".format(args[3]),
                priority=MAIL_PRIORITY.now
            )

            translation.activate(cur_language)

        elif args[0] == 'DONE':

            # notify owner
            cur_language = translation.get_language()
            user_language =  get_user_language(args[1])
            translation.activate(user_language)

            send_html_email_with_dj_template(
                args[1], dj_template='notifications/notify_user_on_successfull_archiving.html',
                context = {
                    'email': args[1],
                    'repo_id': args[2],
                    'repo_name': args[3],
                    'version': args[4],
                },
                subject="Your library has been successfully archived",
                priority=MAIL_PRIORITY.now
            )

            translation.activate(cur_language)
        else:
           logger.warning("Cannot send email on archiving: unknown status: {}".format(args[0]))
