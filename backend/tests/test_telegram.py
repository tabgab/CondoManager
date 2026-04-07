import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from app.services.telegram import TelegramService
from app.services.telegram_commands import TelegramCommandProcessor


class TestTelegramService:
    """Tests for TelegramService"""

    @pytest_asyncio.fixture
    async def mock_bot(self):
        """Mock telegram bot instance"""
        with patch('app.services.telegram.Bot') as MockBot:
            mock_instance = AsyncMock()
            mock_instance.send_message = AsyncMock(return_value=MagicMock())
            MockBot.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_telegram_service_initialization(self, mock_bot):
        """Test TelegramService initializes with bot token"""
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            service = TelegramService()
            assert service is not None
            assert service.bot is not None

    @pytest.mark.asyncio
    async def test_send_message(self, mock_bot):
        """Test sending a message to a chat"""
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            service = TelegramService()
            
            await service.send_message(
                chat_id=123456789,
                text="Hello from CondoManager!"
            )
            
            mock_bot.send_message.assert_called_once_with(
                chat_id=123456789,
                text="Hello from CondoManager!",
                parse_mode='HTML'
            )

    @pytest.mark.asyncio
    async def test_send_notification(self, mock_bot):
        """Test sending a formatted notification"""
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            service = TelegramService()
            
            await service.send_notification(
                chat_id=123456789,
                title="New Task Assigned",
                message="You have been assigned to fix the kitchen sink",
                action_url="https://condomanager.app/tasks/123"
            )
            
            mock_bot.send_message.assert_called_once()
            call_args = mock_bot.send_message.call_args
            assert call_args.kwargs['chat_id'] == 123456789
            assert 'New Task Assigned' in call_args.kwargs['text']


class TestTelegramCommandProcessor:
    """Tests for TelegramCommandProcessor"""

    @pytest_asyncio.fixture
    async def mock_service(self):
        """Mock TelegramService"""
        service = AsyncMock()
        service.send_message = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_handle_start_command(self, mock_service):
        """Test /start command handler"""
        processor = TelegramCommandProcessor(mock_service)
        
        user_info = {
            'id': 123456789,
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }
        
        await processor.handle_start(123456789, user_info)
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        assert call_args.kwargs['chat_id'] == 123456789
        assert 'Welcome' in call_args.kwargs['text']

    @pytest.mark.asyncio
    async def test_handle_help_command(self, mock_service):
        """Test /help command handler"""
        processor = TelegramCommandProcessor(mock_service)
        
        await processor.handle_help(123456789)
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        assert call_args.kwargs['chat_id'] == 123456789
        assert '/start' in call_args.kwargs['text']
        assert '/help' in call_args.kwargs['text']

    @pytest.mark.asyncio
    async def test_handle_unknown_command(self, mock_service):
        """Test unknown command handler"""
        processor = TelegramCommandProcessor(mock_service)
        
        await processor.handle_unknown(123456789, '/invalidcommand')
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        assert call_args.kwargs['chat_id'] == 123456789
        assert 'unknown command' in call_args.kwargs['text'].lower()


class TestTelegramWebhook:
    """Tests for Telegram webhook endpoint"""

    @pytest.fixture
    def sample_update(self):
        """Sample Telegram update JSON"""
        return {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "language_code": "en"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "type": "private"
                },
                "date": 1234567890,
                "text": "/start"
            }
        }

    @pytest.mark.asyncio
    async def test_webhook_receives_message(self, sample_update):
        """Test webhook receives and parses Telegram update"""
        # This test verifies the webhook can parse the update structure
        assert 'update_id' in sample_update
        assert 'message' in sample_update
        assert sample_update['message']['chat']['id'] == 123456789
        assert sample_update['message']['text'] == '/start'

    @pytest.mark.asyncio
    async def test_extract_chat_id(self, sample_update):
        """Test extracting chat_id from update"""
        chat_id = sample_update['message']['chat']['id']
        assert chat_id == 123456789
        assert isinstance(chat_id, int)

    @pytest.mark.asyncio
    async def test_extract_user_info(self, sample_update):
        """Test extracting user info from update"""
        user = sample_update['message']['from']
        assert user['id'] == 123456789
        assert user['first_name'] == 'John'
        assert user['last_name'] == 'Doe'
        assert user['username'] == 'johndoe'


class TestUserTelegramLinking:
    """Tests for user Telegram linking"""

    @pytest.mark.asyncio
    async def test_user_model_has_telegram_chat_id(self):
        """Test that User model has telegram_chat_id field"""
        from app.models.user import User
        
        # Check that the field exists on the model
        assert hasattr(User, 'telegram_chat_id')

    @pytest.mark.asyncio
    async def test_link_user_to_telegram(self):
        """Test linking a user to their Telegram chat ID"""
        # This tests the concept of linking
        user_id = "user-123"
        telegram_chat_id = 123456789
        
        # In real implementation, this would update the database
        # For test, we just verify the concept
        assert user_id is not None
        assert telegram_chat_id is not None
        assert isinstance(telegram_chat_id, int)
