import os
from mailin import Mailin


def send_email_async(subject, to_email, content):
    m = Mailin("https://api.sendinblue.com/v2.0", os.getenv('SENDINBLUE_API_KEY'))
    data = {
        "to": {to_email: "to maintainer!"},
        "from": [os.getenv('PROJECT_MAINTAINER'), "from email!"],
        "subject": subject,
        "html": "<h1>" + content + "</h1>",
    }
    m.send_email(data)
