from zappa.async import task
import sendgrid
from raven import Client
from sendgrid.helpers.mail import Email, Content, Mail
import os


class conditional_task(object):
    def __init__(self, dec):
        self.decorator = dec

    def __call__(self, func):
        if not os.environ.get('AWS_LAMBDA_AVAILABLE', False):
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)


# TODO: move
def send_email(subject, to_email, content):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDGRID_FROM'))
    email = Email(to_email)
    content = Content("text/html", content)
    mail = Mail(from_email, subject, email, content)
    sg.client.mail.send.post(request_body=mail.get())


@conditional_task(task)
def send_email_async(subject, to_email, content):
    send_email(subject, to_email, content)


LAST_VERSION = 'V34.20170902'


def check_if_new_available_feed():
    from scl_transport.etl import get_available_feed, GTFS, FileInfoParser, FeedAnalyzer
    client = Client()
    try:
        available_feed = get_available_feed()

        path = os.path.realpath(os.path.join(__file__, '..', 'etl', 'feed', LAST_VERSION))
        last_loaded_feed = GTFS(data=FileInfoParser(path))
        feed_analyzer = FeedAnalyzer(available_feed, last_loaded_feed)
        report = feed_analyzer.equal_to()
        if not report['version_match']:
            msg = 'New available feed {}'.format(available_feed.version)
            send_email_async(subject=msg, to_email='hermosillavenegas@gmail.com', content=msg)
    except Exception:
        client.captureException()
