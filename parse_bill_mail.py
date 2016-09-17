#!/usr/bin/env python3

import sys
import os
import email
import imaplib
import smtplib
import mimetypes

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64
from email.header import Header
from bs4 import BeautifulSoup


mail = imaplib.IMAP4_SSL('imap.outlook.com')
mail.login('email', 'passwd')
mail.select("Inbox")

#for num in bytes.decode(mail.search(None,'ALL')[1][0]).split(' '):
for num in bytes.decode(mail.search(None,'ALL')[1][0]).split(' '):
    if num != '':
        data = mail.fetch(num, 'RFC822')





