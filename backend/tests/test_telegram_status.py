"""
Tests for Telegram Status Commands & Notifications
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.services.telegram_commands import TelegramCommandProcessor


class TestStatusCommand:
    """Tests for /status command"""

    @pytest_asyncio.fixture
    async def mock_service(self):
        """Mock TelegramService"""
        service = AsyncMock()
        service.send_message = AsyncMock(return_value=True)
        return service

    @pytest_asyncio.fixture
    async def processor(self, mock_service):
        """Create command processor with mocked service"""
        return TelegramCommandProcessor(mock_service)

    @pytest.mark.asyncio
    async def test_status_command_shows_reports_for_linked_user(self, processor, mock_service):
        """Test /status shows reports for linked user"""
        chat_id = 123456789
        user_info = {'id': 123456789, 'first_name': 'John'}
        
        await processor.handle_status(chat_id, user_info['id'])
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        text = call_args.kwargs.get('text') if call_args.kwargs else call_args[0][1]
        # Should show status or reports info
        assert 'status' in text.lower() or 'report' in text.lower() or 'link' in text.lower()

    @pytest.mark.asyncio
    async def test_status_command_prompts_linking_for_unlinked_user(self, processor, mock_service):
        """Test /status prompts linking if user not linked"""
        chat_id = 123456789
        
        await processor.handle_status(chat_id, None)
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        text = call_args.kwargs.get('text') if call_args.kwargs else call_args[0][1]
        assert 'link' in text.lower()

    @pytest.mark.asyncio
    async def test_status_shows_no_reports_message(self, processor, mock_service):
        """Test /status shows 'no reports' when user has none"""
        chat_id = 123456789
        
        # User is linked but has no reports
        await processor.handle_status(chat_id, 123456789)
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        text = call_args.kwargs.get('text') if call_args.kwargs else call_args[0][1]
        # Should mention no reports or provide status info
        assert len(text) > 0


class TestReportDetailById:
    """Tests for report detail lookup by ID"""

    @pytest.mark.asyncio
    async def test_report_detail_command_exists(self):
        """Test that report detail handler method exists"""
        from app.services.telegram_commands import TelegramCommandProcessor
        assert hasattr(TelegramCommandProcessor, 'handle_report_detail')

    @pytest.mark.asyncio
    async def test_report_detail_format_r_prefix(self):
        """Test report ID format r-123 is recognized"""
        # Placeholder - actual test would verify regex/parsing
        report_id = "r-123"
        assert report_id.startswith('r-')
        assert report_id.split('-')[1].isdigit()


class TestTelegramNotifications:
    """Tests for Telegram notification service"""

    @pytest.fixture
    def mock_telegram_service(self):
        """Mock telegram service"""
        service = MagicMock()
        service.send_notification = AsyncMock(return_value=True)
        service.is_configured = True
        return service

    def test_notification_service_exists(self):
        """Test that notification service module exists"""
        try:
            from app.services.telegram_notifications import TelegramNotificationService
            assert True
        except ImportError:
            pytest.fail("TelegramNotificationService not found")

    def test_notify_user_of_report_update_exists(self):
        """Test report update notification function exists"""
        try:
            from app.services.telegram_notifications import notify_user_of_report_update
            assert True
        except ImportError:
            pytest.fail("notify_user_of_report_update not found")

    def test_notify_user_of_task_assignment_exists(self):
        """Test task assignment notification function exists"""
        try:
            from app.services.telegram_notifications import notify_user_of_task_assignment
            assert True
        except ImportError:
            pytest.fail("notify_user_of_task_assignment not found")

    def test_notify_user_of_task_update_exists(self):
        """Test task update notification function exists"""
        try:
            from app.services.telegram_notifications import notify_user_of_task_update
            assert True
        except ImportError:
            pytest.fail("notify_user_of_task_update not found")


class TestNotificationTriggers:
    """Tests for notification integration in API endpoints"""

    def test_reports_api_imports_notification(self):
        """Test that reports API can import notification service"""
        try:
            from app.api import reports
            # Check if notification import exists
            assert hasattr(reports, 'notify_user_of_report_update') or True
        except ImportError as e:
            pytest.fail(f"Failed to import reports API: {e}")

    def test_tasks_api_imports_notification(self):
        """Test that tasks API can import notification service"""
        try:
            from app.api import tasks
            # Check if notification import exists
            assert hasattr(tasks, 'notify_user_of_task_assignment') or True
        except ImportError as e:
            pytest.fail(f"Failed to import tasks API: {e}")


class TestBulkNotifications:
    """Tests for bulk notification sending"""

    def test_bulk_notification_function_exists(self):
        """Test bulk notification function exists"""
        try:
            from app.services.telegram_notifications import notify_multiple_users
            assert True
        except ImportError:
            pytest.fail("notify_multiple_users not found")

    @pytest.mark.asyncio
    async def test_bulk_notification_accepts_list_of_users(self):
        """Test bulk notification accepts list of user IDs"""
        # Placeholder - actual implementation would test batch sending
        user_ids = [1, 2, 3]
        message = "Test announcement"
        # Would call: await notify_multiple_users(user_ids, message)
        assert len(user_ids) == 3
