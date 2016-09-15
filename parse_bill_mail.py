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
mail.login('winstarwang@outlook.com', 'win8@@)!^')
mail.select("&T+F1KFNhjSZTVQ-")

#for num in bytes.decode(mail.search(None,'ALL')[1][0]).split(' '):
for num in bytes.decode(mail.search(None,'ALL')[1][0]).split(' '):
    if num != '':
        data = mail.fetch(num, 'RFC822')



#初始化接收邮件类
# rml = mailUtils.ReceiveMailDealer('winstarwang@outlook.com','win8@@)!^','imap.outlook.com')
# print(rml.show_folders())
# rml.select("&T+F1KFNhjSZTVQ-")
# #print(rml.mail.utf8_enabled)
# #rml.mail.enable("UTF8=ACCEPT")
# print(rml.search(None,'ALL'))
# print(type(rml.mail))

# for num in bytes.decode(rml.search(None,'ALL')[1][0]).split(' '):
#     if num != '':
#         mailInfo = rml.get_mail_info(num)
#         print(mailInfo['subject'])
#         print(mailInfo['body'])
#         print(mailInfo['html'])
#         print(mailInfo['from'])
#         print(mailInfo['to'])
#         #遍历附件列表
#         for attachment in mailInfo['attachments']:
#             fileob = open(attachment['name'],'wb')
#             fileob.write(attachment['data'])
#             fileob.close()




