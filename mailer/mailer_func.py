# import os
#
# from mailersend import emails
# from dotenv import load_dotenv
#
# load_dotenv()
#
# mailer = emails.NewEmail(os.getenv('MAILER_API_KEY'))
# mail_body = {}
#
# mail_from = {
#     "name": "Cryptex LTD",
#     "email": "MS_HBuAI2@trial-jy7zpl93v6pl5vx6.mlsender.net"
# }
#
# bcc_recipients = [
#     {
#         "name": "Client Name",
#         "email": "iamanaiyelu@gmail.com"
#     }
# ]
#
# reply_to = {
#     "name": "Cryptex Support",
#     "email": "iamanaiyeludaniel@gmail.com"
# }

import smtplib
import urllib.parse

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject: str, html_content: str, recipient: list):
    me = "account@atlaswavestrader.com"
    you = recipient[0]["email"]

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = recipient[0]["email"]
    part2 = MIMEText(html_content, "html")

    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('mail.atlaswavestrader.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()
    mail.login('account@atlaswavestrader', "Lucifer,.123")
    mail.sendmail(me, you, msg.as_string())
    mail.quit()


