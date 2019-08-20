from django.test import TestCase
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# Create your tests here.
class UnitTest(TestCase):
    def testGetSites(self):
        my_sender = '1421606162@qq.com'  # 发件人邮箱账号
        my_pass = '@wxb*133'  # 发件人邮箱密码
        my_user = '1421606162@qq.com'  # 收件人邮箱账号，我这边发送给自己
        ret = True
        try:
            print("开始发送")
            msg = MIMEText('填写邮件内容', 'plain', 'utf-8')
            msg['From'] = formataddr(["FromRunoob", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["王彪", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "菜鸟教程发送邮件测试"  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            print("发送成功")
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret = False
            print("")
        return ret









