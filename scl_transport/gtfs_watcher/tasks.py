from .utils import LinkExtractor
from bs4 import BeautifulSoup
from zappa.async import task
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import os

BASE_URL = 'https://www.dtpm.cl/index.php/'
REFERENCE_GTFS = '02-09-2017'


class conditional_task(object):
    def __init__(self, dec):
        self.decorator = dec

    def __call__(self, func):
        if not os.environ.get('AWS_LAMBDA_AVAILABLE', False):
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)


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


def analyze():
    try:
        # get GTFS website link
        link_extractor = LinkExtractor(url=BASE_URL, contains_text="GTFS Vigente")
        # get GTFS website html
        link_extractor = LinkExtractor(url=link_extractor.link)
        # get GTFS text
        soup = BeautifulSoup(link_extractor.response, 'html.parser')
        text_to_analize = soup.findAll('div', {'class': 'item-page'})[0].p.strong.text
        if REFERENCE_GTFS not in text_to_analize:
            msg = 'New available feed: {}'.format(text_to_analize)
            send_email_async(subject=msg, to_email=str(os.getenv('PROJECT_MAINTAINER')), content=msg)
    except Exception:
        msg = 'Error getting GTFS info'
        send_email_async(subject=msg, to_email=str(os.getenv('PROJECT_MAINTAINER')), content=msg)
