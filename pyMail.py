# -*- coding: utf-8 -*-
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

#*********接受邮件部分（IMAP）**********
#处理接受邮件的类
class ReceiveMailDealer:

    #构造函数(用户名，密码，imap服务器)
    def __init__(self, username, password, server):
        self.mail = imaplib.IMAP4_SSL(server)
        self.mail.login(username, password)
        self.select("INBOX")

    #返回所有文件夹
    def show_folders(self):
        return self.mail.list()

    #选择收件箱（如“INBOX”，如果不知道可以调用showFolders）
    def select(self, folder):
        return self.mail.select(folder)

    #搜索邮件(参照RFC文档http://tools.ietf.org/html/rfc3501#page-49)
    def search(self, charset, *criteria):
        try:
            return self.mail.search(charset,*criteria)
        except :
            self.select("INBOX")
            return self.mail.search(charset,*criteria)

    #返回所有未读的邮件列表（返回的是包含邮件序号的列表）
    def get_unread(self):
        return self.search(None,"Unseen")

    #以RFC822协议格式返回邮件详情的email对象
    def get_email_format(self, index):
        data = self.mail.fetch(index, 'RFC822')
        if data[0] == 'OK':
            return email.message_from_string(bytes.decode(data[1][0][1]))
        else:
            return "fetch error"

    #返回发送者的信息——元组（邮件称呼，邮件地址）
    def get_sender_info(self, msg):
        name = email.utils.parseaddr(msg["from"])[0]
        decode_name = email.header.decode_header(name)[0]
        if decode_name[1] != None:
            name = (decode_name[0], decode_name[1])
        address = email.utils.parseaddr(msg["from"])[1]
        return (name, address)

    #返回接受者的信息——元组（邮件称呼，邮件地址）
    def get_receiver_info(self, msg):
        name = email.utils.parseaddr(msg["to"])[0]
        decode_name = email.header.decode_header(name)[0]
        if decode_name[1] != None:
            name = (decode_name[0], decode_name[1])
        address = email.utils.parseaddr(msg["to"])[1]
        return (name, address)

    #返回邮件的主题（参数msg是email对象，可调用getEmailFormat获得）
    def get_subject_content(self, msg):
        decode_content =  email.header.decode_header(msg['subject'])[0]
        if decode_content[1] != None:
            return (decode_content[0], decode_content[1])
        return decode_content[0]

    '''判断是否有附件，并解析（解析email对象的part）
    返回列表（内容类型，大小，文件名，数据流）
    '''
    def parse_attachment(self, message_part):
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and dispositions[0].lower() == "attachment"):

                file_data = message_part.get_payload(decode=True)
                attachment = {}
                attachment["content_type"] = message_part.get_content_type()
                attachment["size"] = len(file_data)
                decode_name = email.header.decode_header(message_part.get_filename())[0]
                name = decode_name[0]
                if decode_name[1] != None:
                    name = (decode_name[0], decode_name[1])
                print(name)
                attachment["name"] = name
                attachment["data"] = file_data
                '''保存附件
                fileobject = open(name, "wb")
                fileobject.write(file_data)
                fileobject.close()
                '''
                return attachment
        return None

    '''返回邮件的解析后信息部分
    返回列表包含（主题，纯文本正文部分，html的正文部分，发件人元组，收件人元组，附件列表）
    '''
    def get_mail_info(self, index):
        msg = self.get_email_format(index)
        attachments = []
        body = None
        html = None
        for part in msg.walk():
            attachment = self.parse_attachment(part)
            if attachment:
                attachments.append(attachment)
            elif part.get_content_type() == "text/plain":
                if body is None:
                    body = ""
                body += bytes.decode(part.get_payload(decode=True))
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = ""
                html += bytes.decode(part.get_payload(decode=True))
        return {
            'subject' : self.get_subject_content(msg),
            'body' : body,
            'html' : html,
            'from' : self.get_sender_info(msg),
            'to' : self.get_receiver_info(msg),
            'attachments': attachments,
        }


#*********发送邮件部分(smtp)**********

class SendMailDealer:

    #构造函数（用户名，密码，smtp服务器）
    def __init__(self, user, passwd, smtp,port,usettls=False):
        self.mailUser = user
        self.mailPassword = passwd
        self.smtpServer = smtp
        self.smtpPort   = port
        self.mailServer = smtplib.SMTP(self.smtpServer, self.smtpPort)
        self.mailServer.ehlo()
        if usettls:
            self.mailServer.starttls()
        self.mailServer.ehlo()
        self.mailServer.login(self.mailUser, self.mailPassword)
        self.msg = MIMEMultipart()

    #对象销毁时，关闭mailserver
    def __del__(self):
        self.mailServer.close()

    #重新初始化邮件信息部分
    def reinit_mail_info():
        self.msg = MIMEMultipart()

    #设置邮件的基本信息（收件人，主题，正文，正文类型html或者plain，可变参数附件路径列表）
    def set_mail_info(self, receiveUser, subject, text, text_type,*attachmentFilePaths):
        self.msg['From'] = self.mailUser
        self.msg['To'] = receiveUser

        self.msg['Subject'] = subject
        self.msg.attach(MIMEText(text, text_type))
        for attachmentFilePath in attachmentFilePaths:
            self.msg.attach(self.getAttachmentFromFile(attachmentFilePath))

    #自定义邮件正文信息（正文内容，正文格式html或者plain）
    def add_text_part(self, text, text_type):
        self.msg.attach(MIMEText(text, text_type))


    #增加附件（以流形式添加，可以添加网络获取等流格式）参数（文件名，文件流）
    def add_attachment(self, filename, filedata):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(filedata)
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % str(Header(filename, 'utf8')))
        self.msg.attach(part)

    #通用方法添加邮件信息（MIMETEXT，MIMEIMAGE,MIMEBASE...）
    def add_part(self, part):
        self.msg.attach(part)

    # 发送邮件
    def send_mail(self):
        if not self.msg['To']:
            print ("没有收件人,请先设置邮件基本信息")
            return
        self.mailServer.sendmail(self.mailUser, self.msg['To'], self.msg.as_string())
        print('Sent email to %s' % self.msg['To'])


    #通过路径添加附件
    def get_attachment_from_file(self, attachmentFilePath):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(attachmentFilePath,"rb").read())
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % str(Header(attachmentFilePath, 'utf8')))
        return part

