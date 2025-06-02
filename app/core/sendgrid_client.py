from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.settings import SENDGRID_API_KEY
from app.core.utils.logger import logger


class SendgridClient:
    API_KEY = SENDGRID_API_KEY

    def __init__(self):
        self.sg = SendGridAPIClient(self.API_KEY)

    def send_email(
        self,
        to_emails: str,
        subject: str,
        html_content: str,
        from_email: str,
    ):
        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=html_content,
        )
        self._send(message)

    def _send(self, message: Mail):
        try:
            self.sg.send(message)
        except Exception as e:
            logger.error(f"Failed to send email by Sendgrid. Error: {e}")


sendgrid_client = SendgridClient()
