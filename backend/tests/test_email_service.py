"""Email service tests - TDD approach."""
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Set test environment variables before importing
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["EMAIL_PROVIDER"] = "sendgrid"
os.environ["SENDGRID_API_KEY"] = "test-sendgrid-key"
os.environ["RESEND_API_KEY"] = "test-resend-key"
os.environ["DEFAULT_FROM_EMAIL"] = "noreply@condomanager.app"
os.environ["EMAIL_FROM_NAME"] = "CondoManager"

from app.services.email import EmailService, EmailTemplate


class TestEmailServiceInitialization:
    """Test EmailService initialization."""

    def test_init_with_sendgrid(self):
        """EmailService initializes with SendGrid when configured."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            assert service.provider == "sendgrid"
            assert service.from_email == "noreply@condomanager.app"
            assert service.from_name == "CondoManager"

    def test_init_with_resend(self):
        """EmailService initializes with Resend when configured."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "resend"}):
            service = EmailService()
            assert service.provider == "resend"

    def test_init_defaults(self):
        """EmailService uses default values when not configured."""
        with patch.dict(os.environ, {}, clear=False):
            service = EmailService()
            assert service.from_email == "noreply@condomanager.app"
            assert service.from_name == "CondoManager"


class TestEmailServiceSend:
    """Test EmailService send methods."""

    @pytest.mark.asyncio
    async def test_send_email_with_sendgrid(self):
        """Send email using SendGrid API."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            
            # Mock SendGrid client
            mock_response = Mock()
            mock_response.status_code = 202
            service.sg_client = Mock()
            service.sg_client.send = AsyncMock(return_value=mock_response)
            
            result = await service.send_email(
                to_email="user@example.com",
                subject="Test Subject",
                html_content="<h1>Test</h1>",
                text_content="Test content",
            )
            
            assert result is True
            service.sg_client.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_resend(self):
        """Send email using Resend API."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "resend"}):
            service = EmailService()
            
            # Mock Resend client
            mock_response = {"id": "test-email-id"}
            service.resend_client = Mock()
            service.resend_client.emails = Mock()
            service.resend_client.emails.send = Mock(return_value=mock_response)
            
            result = await service.send_email(
                to_email="user@example.com",
                subject="Test Subject",
                html_content="<h1>Test</h1>",
                text_content="Test content",
            )
            
            assert result is True
            service.resend_client.emails.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_fallback_to_resend(self):
        """Fallback to Resend when SendGrid fails."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            
            # Mock SendGrid to fail
            service.sg_client = Mock()
            service.sg_client.send = AsyncMock(side_effect=Exception("SendGrid error"))
            
            # Mock Resend to succeed
            mock_response = {"id": "test-email-id"}
            service.resend_client = Mock()
            service.resend_client.emails = Mock()
            service.resend_client.emails.send = Mock(return_value=mock_response)
            
            result = await service.send_email(
                to_email="user@example.com",
                subject="Test Subject",
                html_content="<h1>Test</h1>",
            )
            
            assert result is True
            service.sg_client.send.assert_called_once()
            service.resend_client.emails.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_no_api_keys(self):
        """Handle missing API keys gracefully."""
        with patch.dict(os.environ, {
            "EMAIL_PROVIDER": "sendgrid",
            "SENDGRID_API_KEY": "",
            "RESEND_API_KEY": "",
        }):
            service = EmailService()
            
            result = await service.send_email(
                to_email="user@example.com",
                subject="Test Subject",
                html_content="<h1>Test</h1>",
            )
            
            assert result is False


class TestEmailTemplates:
    """Test email template rendering."""

    def test_welcome_template_rendering(self):
        """Welcome email template renders correctly."""
        service = EmailService()
        
        context = {
            "user_name": "John Doe",
            "email": "john@example.com",
            "login_url": "https://condomanager.app/login",
        }
        
        html_content, text_content = service.render_template("welcome", context)
        
        assert "John Doe" in html_content
        assert "Welcome" in html_content
        assert "condomanager.app" in html_content
        assert text_content is not None

    def test_task_assigned_template_rendering(self):
        """Task assigned email template renders correctly."""
        service = EmailService()
        
        context = {
            "employee_name": "Jane Smith",
            "task_title": "Fix Broken Pipe",
            "building_name": "Building A",
            "task_url": "https://condomanager.app/tasks/123",
        }
        
        html_content, text_content = service.render_template("task_assigned", context)
        
        assert "Jane Smith" in html_content
        assert "Fix Broken Pipe" in html_content
        assert "Building A" in html_content
        assert text_content is not None

    def test_report_submitted_template_rendering(self):
        """Report submitted email template renders correctly."""
        service = EmailService()
        
        context = {
            "manager_name": "Manager",
            "reporter_name": "Owner",
            "report_title": "Water Leak",
            "building_name": "Building B",
            "report_url": "https://condomanager.app/reports/456",
        }
        
        html_content, text_content = service.render_template("report_submitted", context)
        
        assert "Water Leak" in html_content
        assert "Owner" in html_content
        assert text_content is not None

    def test_invalid_template_name(self):
        """Invalid template name returns None."""
        service = EmailService()
        
        html_content, text_content = service.render_template("nonexistent", {})
        
        assert html_content is None
        assert text_content is None


class TestTemplateEmailSending:
    """Test sending templated emails."""

    @pytest.mark.asyncio
    async def test_send_welcome_email(self):
        """Send welcome email using template."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            
            mock_response = Mock()
            mock_response.status_code = 202
            service.sg_client = Mock()
            service.sg_client.send = AsyncMock(return_value=mock_response)
            
            context = {
                "user_name": "John Doe",
                "email": "john@example.com",
                "login_url": "https://condomanager.app/login",
            }
            
            result = await service.send_template_email(
                to_email="john@example.com",
                template_name="welcome",
                context=context,
            )
            
            assert result is True
            service.sg_client.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_task_completed_email(self):
        """Send task completed email using template."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            
            mock_response = Mock()
            mock_response.status_code = 202
            service.sg_client = Mock()
            service.sg_client.send = AsyncMock(return_value=mock_response)
            
            context = {
                "manager_name": "Manager",
                "employee_name": "Employee",
                "task_title": "Clean Hallway",
                "task_url": "https://condomanager.app/tasks/123",
            }
            
            result = await service.send_template_email(
                to_email="manager@example.com",
                template_name="task_completed",
                context=context,
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_send_report_acknowledged_email(self):
        """Send report acknowledged email using template."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            
            mock_response = Mock()
            mock_response.status_code = 202
            service.sg_client = Mock()
            service.sg_client.send = AsyncMock(return_value=mock_response)
            
            context = {
                "owner_name": "Owner",
                "report_title": "Noise Complaint",
                "report_url": "https://condomanager.app/reports/456",
            }
            
            result = await service.send_template_email(
                to_email="owner@example.com",
                template_name="report_acknowledged",
                context=context,
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_send_weekly_summary_email(self):
        """Send weekly summary email using template."""
        with patch.dict(os.environ, {"EMAIL_PROVIDER": "sendgrid"}):
            service = EmailService()
            
            mock_response = Mock()
            mock_response.status_code = 202
            service.sg_client = Mock()
            service.sg_client.send = AsyncMock(return_value=mock_response)
            
            context = {
                "manager_name": "Manager",
                "completed_tasks": 5,
                "pending_tasks": 3,
                "new_reports": 2,
                "dashboard_url": "https://condomanager.app/dashboard",
            }
            
            result = await service.send_template_email(
                to_email="manager@example.com",
                template_name="weekly_summary",
                context=context,
            )
            
            assert result is True
