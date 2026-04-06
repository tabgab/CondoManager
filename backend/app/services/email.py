"""Email service using SendGrid (primary) with Resend fallback."""
import logging
import re
from typing import Optional, Tuple
from jinja2 import Template
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service supporting SendGrid (primary) and Resend (fallback)."""
    
    def __init__(self):
        """Initialize email service with configured provider."""
        settings = get_settings()
        self.provider = settings.EMAIL_PROVIDER.lower()
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.from_name = settings.EMAIL_FROM_NAME
        self.sg_api_key = settings.SENDGRID_API_KEY
        self.resend_api_key = settings.RESEND_API_KEY
        self.sg_client = None
        self.resend_client = None
        
        if self.provider == "sendgrid" and self.sg_api_key:
            try:
                from sendgrid import SendGridAPIClient
                self.sg_client = SendGridAPIClient(self.sg_api_key)
            except Exception as e:
                logger.warning(f"SendGrid init failed: {e}")
        
        if self.resend_api_key:
            try:
                import resend
                resend.api_key = self.resend_api_key
                self.resend_client = resend
            except Exception as e:
                logger.warning(f"Resend init failed: {e}")
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using configured provider with fallback."""
        if text_content is None:
            text_content = self._html_to_text(html_content)
        
        if self.provider == "sendgrid" and self.sg_client:
            try:
                from sendgrid.helpers.mail import Mail, From, To, Content, MimeType
                message = Mail(
                    from_email=From(self.from_email, self.from_name),
                    to_emails=To(to_email),
                    subject=subject,
                    html_content=Content(MimeType.html, html_content),
                )
                message.add_content(Content(MimeType.text, text_content))
                response = self.sg_client.send(message)
                if response.status_code in (200, 201, 202):
                    return True
            except Exception as e:
                logger.warning(f"SendGrid failed: {e}")
        
        if self.resend_client:
            try:
                params = {
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                    "text": text_content,
                }
                response = self.resend_client.Emails.send(params)
                if response and response.get("id"):
                    return True
            except Exception as e:
                logger.error(f"Resend failed: {e}")
        
        return False
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text."""
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def render_template(self, template_name: str, context: dict) -> Tuple[Optional[str], Optional[str]]:
        """Render email template with context."""
        templates = {
            "welcome": self._welcome_template(),
            "task_assigned": self._task_assigned_template(),
            "task_completed": self._task_completed_template(),
            "report_submitted": self._report_submitted_template(),
            "report_acknowledged": self._report_acknowledged_template(),
            "weekly_summary": self._weekly_summary_template(),
        }
        template_html = templates.get(template_name)
        if not template_html:
            return None, None
        try:
            template = Template(template_html)
            html = template.render(**context)
            text = self._html_to_text(html)
            return html, text
        except Exception as e:
            logger.error(f"Template error: {e}")
            return None, None
    
    async def send_template_email(self, to_email: str, template_name: str, context: dict, subject: Optional[str] = None) -> bool:
        """Send templated email."""
        html, text = self.render_template(template_name, context)
        if not html:
            return False
        if not subject:
            subject = self._generate_subject(template_name, context)
        return await self.send_email(to_email, subject, html, text)
    
    def _generate_subject(self, template_name: str, context: dict) -> str:
        """Generate email subject."""
        subjects = {
            "welcome": f"Welcome to CondoManager, {context.get('user_name', 'there')}!",
            "task_assigned": f"New Task: {context.get('task_title', 'Task')}",
            "task_completed": f"Completed: {context.get('task_title', 'Task')}",
            "report_submitted": f"New Report: {context.get('report_title', 'Issue')}",
            "report_acknowledged": f"Report Received: {context.get('report_title', 'Issue')}",
            "weekly_summary": "Weekly CondoManager Summary",
        }
        return subjects.get(template_name, "CondoManager Notification")
    
    def _base(self, title: str, body: str) -> str:
        return f"<html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;'><div style='background:#4a90d9;color:white;padding:20px;text-align:center;'><h1>CondoManager</h1></div><div style='padding:20px;border:1px solid #ddd;'><h2>{title}</h2>{body}</div><div style='background:#333;color:white;padding:15px;text-align:center;font-size:12px;'>CondoManager - Do not reply</div></body></html>"
    
    def _welcome_template(self) -> str:
        return self._base("Welcome!", "<p>Hello {{ user_name }},</p><p>Welcome to CondoManager!</p><p>Email: {{ email }}</p><p><a href='{{ login_url }}' style='background:#4a90d9;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;'>Log In</a></p>")
    
    def _task_assigned_template(self) -> str:
        return self._base("New Task Assigned", "<p>Hi {{ employee_name }},</p><p>You have been assigned: <strong>{{ task_title }}</strong></p><p>Building: {{ building_name }}</p><p><a href='{{ task_url }}' style='background:#4a90d9;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;'>View Task</a></p>")
    
    def _task_completed_template(self) -> str:
        return self._base("Task Completed", "<p>Hi {{ manager_name }},</p><p>{{ employee_name }} completed: <strong>{{ task_title }}</strong></p><p><a href='{{ task_url }}' style='background:#4a90d9;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;'>Review Task</a></p>")
    
    def _report_submitted_template(self) -> str:
        return self._base("New Report Submitted", "<p>Hi {{ manager_name }},</p><p>{{ reporter_name }} submitted: <strong>{{ report_title }}</strong></p><p>Building: {{ building_name }}</p><p><a href='{{ report_url }}' style='background:#4a90d9;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;'>View Report</a></p>")
    
    def _report_acknowledged_template(self) -> str:
        return self._base("Report Acknowledged", "<p>Hi {{ owner_name }},</p><p>Your report has been received: <strong>{{ report_title }}</strong></p><p><a href='{{ report_url }}' style='background:#4a90d9;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;'>View Report</a></p>")
    
    def _weekly_summary_template(self) -> str:
        return self._base("Weekly Summary", "<p>Hi {{ manager_name }},</p><p>Weekly summary:</p><ul><li>Completed: {{ completed_tasks }}</li><li>Pending: {{ pending_tasks }}</li><li>New reports: {{ new_reports }}</li></ul><p><a href='{{ dashboard_url }}' style='background:#4a90d9;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;'>View Dashboard</a></p>")


class EmailTemplate:
    """Template name constants."""
    WELCOME = "welcome"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    REPORT_SUBMITTED = "report_submitted"
    REPORT_ACKNOWLEDGED = "report_acknowledged"
    WEEKLY_SUMMARY = "weekly_summary"
