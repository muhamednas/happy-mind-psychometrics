import logging
import os

from app.config import settings

logger = logging.getLogger("app.email_service")


class EmailService:
    @staticmethod
    async def send_nudge_email(email: str, name: str, access_code: str, package_title: str) -> bool:
        """Send a transactional "please complete your assessment" nudge.

        Uses SendGrid or AWS SES when configured via env; otherwise logs the
        email content (local-development simulation) and returns True. The
        provider SDKs are imported lazily so they are not hard dependencies.
        """
        subject = f"Friendly Reminder: Complete your {package_title} assessment"
        portal_url = settings.PORTAL_URL

        body_text = (
            f"Hello {name},\n\n"
            f"This is a friendly reminder to complete your '{package_title}' assessment.\n"
            f"Please log in to the assessment portal using your access code: {access_code}\n\n"
            f"Portal Link: {portal_url}\n\n"
            f"Best regards,\n"
            f"The Happy Mind Team"
        )
        body_html = (
            "<div style='font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; "
            "border: 1px solid #e2e8f0; border-radius: 8px;'>"
            "<h2 style='color: #4f46e5;'>Friendly Reminder</h2>"
            f"<p>Hello <strong>{name}</strong>,</p>"
            f"<p>This is a friendly reminder to complete your <strong>{package_title}</strong> assessment.</p>"
            "<div style='margin: 20px 0; padding: 15px; background-color: #f8fafc; "
            "border-left: 4px solid #4f46e5; font-family: monospace;'>"
            f"Access Code: <strong style='font-size: 1.1rem; color: #1e1b4b;'>{access_code}</strong>"
            "</div>"
            f"<p><a href='{portal_url}' style='display: inline-block; padding: 10px 20px; "
            "background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; "
            "font-weight: bold;'>Go to Portal</a></p>"
            "<p style='color: #64748b; font-size: 0.875rem; margin-top: 30px;'>Best regards,<br>"
            "The Happy Mind Team</p>"
            "</div>"
        )

        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        aws_ses_region = os.getenv("AWS_SES_REGION")

        if sendgrid_api_key:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail

                message = Mail(
                    from_email="no-reply@happymind.com",
                    to_emails=email,
                    subject=subject,
                    html_content=body_html,
                )
                SendGridAPIClient(sendgrid_api_key).send(message)
                logger.info("SendGrid email sent to %s", email)
                return True
            except Exception as exc:  # noqa: BLE001 - provider errors shouldn't 500 the caller
                logger.error("SendGrid send failed: %s", exc)
                return False

        if aws_ses_region:
            try:
                import boto3

                boto3.client("ses", region_name=aws_ses_region).send_email(
                    Source="no-reply@happymind.com",
                    Destination={"ToAddresses": [email]},
                    Message={
                        "Subject": {"Data": subject},
                        "Body": {"Text": {"Data": body_text}, "Html": {"Data": body_html}},
                    },
                )
                logger.info("AWS SES email sent to %s", email)
                return True
            except Exception as exc:  # noqa: BLE001
                logger.error("AWS SES send failed: %s", exc)
                return False

        # Local-development simulation (no provider configured).
        logger.info("=" * 60)
        logger.info("SIMULATING EMAIL DISPATCH (no email provider configured)")
        logger.info("Recipient: %s", email)
        logger.info("Subject: %s", subject)
        logger.info("Content:\n%s", body_text)
        logger.info("=" * 60)
        return True
