import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from app.utils.logger import setup_logger
from app.utils.config import ConfigLoader
import os

class EmailSender:
    def __init__(self, logger=None):
        self.logger = logger if logger else setup_logger()
        self.config = ConfigLoader("app/utils/config/config.json")
        self.enabled = self.config.get("email_notifications")

    def send_notification(self, subject, body, attachments=None):
        if self.enabled:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.config['email']['sender']
                msg['To'] = self.config['email']['recipient']
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                if attachments:
                    for attachment in attachments:
                        with open(attachment, "rb") as file:
                            part = MIMEApplication(file.read(), Name=os.path.basename(attachment))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                        msg.attach(part)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(self.config['email']['sender'], self.config['email']['password'])
                server.sendmail(self.config['email']['sender'], self.config['email']['recipient'], msg.as_string())
                server.quit()

                self.logger.info("Email notification sent with CSV attachments.")
            except Exception as e:
                self.logger.error(f"Failed to send email notification: {e}")