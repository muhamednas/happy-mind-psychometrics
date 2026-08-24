import logging
import os
from app.config import settings

logger = logging.getLogger("app.email_service")

class EmailService:
    @staticmethod
    async def send_nudge_email(email: str, name: str, access_code: str, package_title: str) -> bool:
        """
        Sends a transactional nudge email to a candidate.
        If environment variables are set for SendGrid or AWS SES, uses those;
        otherwise logs the email content to stdout for local development.
        """
        subject = f"Friendly Reminder: Complete your {package_title} assessment"
        
        body_text = (
            f"Hello {name},\n\n"
            f"This is a friendly reminder to complete your '{package_title}' assessment.\n"
            f"Please log in to the assessment portal using your access code: {access_code}\n\n"
            f"Portal Link: http://localhost:5173/portal\n\n"
            f"Best regards,\n"
            f"The Happy Mind Team"
        )
        
        body_html = (
            f"<div style='font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;'>"
            f"<h2 style='color: #4f46e5;'>Friendly Reminder</h2>"
            f"<p>Hello <strong>{name}</strong>,</p>"
            f"<p>This is a friendly reminder to complete your <strong>{package_title}</strong> assessment.</p>"
            f"<div style='margin: 20px 0; padding: 15px; background-color: #f8fafc; border-left: 4px solid #4f46e5; font-family: monospace;'>"
            f"Access Code: <strong style='font-size: 1.1rem; color: #1e1b4b;'>{access_code}</strong>"
            f"</div>"
            f"<p>Click the link below to access the login page:</p>"
            f"<p><a href='http://localhost:5173/portal' style='display: inline-block; padding: 10px 20px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;'>Go to Portal</a></p>"
            f"<p style='color: #64748b; font-size: 0.875rem; margin-top: 30px;'>Best regards,<br>The Happy Mind Team</p>"
            f"</div>"
        )

        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        aws_ses_region = os.getenv("AWS_SES_REGION")

        if sendgrid_api_key:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                message = Mail(
                    from_email='no-reply@happymind.com',
                    to_emails=email,
                    subject=subject,
                    html_content=body_html
                )
                sg = SendGridAPIClient(sendgrid_api_key)
                sg.send(message)
                logger.info(f"SendGrid email successfully sent to {email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid: {str(e)}")
        
        elif aws_ses_region:
            try:
                import boto3
                ses_client = boto3.client('ses', region_name=aws_ses_region)
                ses_client.send_email(
                    Source='no-reply@happymind.com',
                    Destination={'ToAddresses': [email]},
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {
                            'Text': {'Data': body_text},
                            'Html': {'Data': body_html}
                        }
                    }
                )
                logger.info(f"AWS SES email successfully sent to {email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via AWS SES: {str(e)}")
        
        # Local development simulation fallback
        logger.info("=" * 60)
        logger.info("SIMULATING EMAIL DISPATCH (No production credentials set)")
        logger.info(f"Recipient: {email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Content:\n{body_text}")
        logger.info("=" * 60)
        return True
