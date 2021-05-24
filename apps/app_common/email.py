
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template import loader
from django.conf import settings
import threading



class SendHtmlEmail(threading.Thread):
    """send html email"""
    def __init__(self, subject, html_content, send_from, to_list, fail_silently = True):
        super(SendHtmlEmail, self).__init__()
        # super().__init__()
        self.subject = subject
        self.html_content = html_content
        self.send_from = send_from
        self.to_list = to_list
        self.fail_silently = fail_silently  # 默认发送异常不报错
        self.daemon = True

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.send_from, self.to_list)
        msg.content_subtype = "html"  # 设置类型为html
        result = msg.send(self.fail_silently)
        print(result)


def send_email_by_template(subject, temp_name, data, to_list):
    """
    使用模版发送邮件
        subject:    string, 主题
        temp_name:  string, 模版名称
        data:       dict,   数据
        to_list:    list,   收件人
    """
    html_content = loader.render_to_string(temp_name, data)
    return send_html_email(subject, html_content, to_list)


def send_html_email(subject, html_content, to_list):
    """发送html邮件"""
    send_from = settings.EMAIL_HOST_USER
    send_email = SendHtmlEmail(subject, html_content, send_from, to_list)
    send_email.start()