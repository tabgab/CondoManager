"""
Tests for Telegram Report Submission Command
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.services.telegram_conversations import (
    ConversationStore,
    ConversationState,
    get_conversation_store
)
from app.services.telegram_commands import TelegramCommandProcessor


class TestConversationStore:
    """Tests for conversation state storage"""

    @pytest.fixture
    def store(self):
        """Create fresh conversation store"""
        return ConversationStore()

    def test_start_conversation(self, store):
        """Test starting a new conversation"""
        chat_id = 123456789
        store.start_conversation(chat_id)
        
        state = store.get_state(chat_id)
        assert state is not None
        assert state['state'] == ConversationState.AWAITING_TITLE
        assert state['data'] == {}

    def test_get_state_nonexistent(self, store):
        """Test getting state for non-existent conversation"""
        state = store.get_state(999999999)
        assert state is None

    def test_update_state(self, store):
        """Test updating conversation state"""
        chat_id = 123456789
        store.start_conversation(chat_id)
        
        store.update_state(chat_id, ConversationState.AWAITING_DESCRIPTION, {'title': 'Test'})
        
        state = store.get_state(chat_id)
        assert state['state'] == ConversationState.AWAITING_DESCRIPTION
        assert state['data']['title'] == 'Test'

    def test_end_conversation(self, store):
        """Test ending a conversation"""
        chat_id = 123456789
        store.start_conversation(chat_id)
        
        store.end_conversation(chat_id)
        
        state = store.get_state(chat_id)
        assert state is None

    def test_conversation_data_accumulation(self, store):
        """Test that conversation data accumulates across updates"""
        chat_id = 123456789
        store.start_conversation(chat_id)
        
        store.update_state(chat_id, ConversationState.AWAITING_CATEGORY, {'title': 'Leak'})
        store.update_state(chat_id, ConversationState.AWAITING_DESCRIPTION, {'category': 'maintenance'})
        
        state = store.get_state(chat_id)
        assert state['data']['title'] == 'Leak'
        assert state['data']['category'] == 'maintenance'


class TestReportCommandFlow:
    """Tests for /report command conversation flow"""

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
    async def test_report_command_starts_conversation(self, processor, mock_service):
        """Test /report command initiates report flow"""
        chat_id = 123456789
        user_info = {'id': 123456789, 'first_name': 'John'}
        
        await processor.handle_report_start(chat_id, user_info)
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        # Handle both positional and keyword arguments
        if call_args.kwargs:
            assert call_args.kwargs['chat_id'] == chat_id
            assert 'title' in call_args.kwargs['text'].lower()
        else:
            assert call_args[0][0] == chat_id
            assert 'title' in call_args[0][1].lower()

    @pytest.mark.asyncio
    async def test_conversation_awaits_category_after_title(self, processor, mock_service):
        """Test after title input, bot asks for category"""
        chat_id = 123456789
        
        # Start conversation
        await processor.handle_report_start(chat_id, {'id': 123456789})
        mock_service.send_message.reset_mock()
        
        # Send title
        await processor.handle_conversation_message(chat_id, 'Kitchen leak', {'id': 123456789})
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        # Handle both positional and keyword arguments
        text = call_args.kwargs.get('text') if call_args.kwargs else call_args[0][1]
        assert 'category' in text.lower() or 'select' in text.lower()

    @pytest.mark.asyncio
    async def test_conversation_awaits_description_after_category(self, processor, mock_service):
        """Test after category selection, bot asks for description"""
        chat_id = 123456789
        
        # Simulate up to category selection
        await processor.handle_report_start(chat_id, {'id': 123456789})
        await processor.handle_conversation_message(chat_id, 'Kitchen leak', {'id': 123456789})
        mock_service.send_message.reset_mock()
        
        # Send category number
        await processor.handle_conversation_message(chat_id, '1', {'id': 123456789})
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        # Handle both positional and keyword arguments
        text = call_args.kwargs.get('text') if call_args.kwargs else call_args[0][1]
        assert 'describe' in text.lower() or 'description' in text.lower()

    @pytest.mark.asyncio
    async def test_conversation_shows_summary_after_description(self, processor, mock_service):
        """Test after description, bot shows summary"""
        chat_id = 123456789
        
        # Simulate up to description
        await processor.handle_report_start(chat_id, {'id': 123456789})
        await processor.handle_conversation_message(chat_id, 'Kitchen leak', {'id': 123456789})
        await processor.handle_conversation_message(chat_id, '1', {'id': 123456789})
        mock_service.send_message.reset_mock()
        
        # Send description
        await processor.handle_conversation_message(chat_id, 'Water leaking under sink', {'id': 123456789})
        
        mock_service.send_message.assert_called_once()
        call_args = mock_service.send_message.call_args
        # Handle both positional and keyword arguments
        text = call_args.kwargs.get('text') if call_args.kwargs else call_args[0][1]
        assert 'summary' in text.lower() or 'confirm' in text.lower() or 'yes' in text.lower()


class TestUserLinking:
    """Tests for Telegram user linking"""

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_chat_id(self):
        """Test finding user by telegram_chat_id"""
        # This is a placeholder - actual implementation would query database
        chat_id = 123456789
        
        # In real implementation, this would call CRUD function
        # For test, we verify the function signature exists
        from app.services.telegram_commands import TelegramCommandProcessor
        assert hasattr(TelegramCommandProcessor, 'get_or_create_user_by_telegram')


class TestPhotoHandling:
    """Tests for photo attachments in reports"""

    @pytest.mark.asyncio
    async def test_photo_in_report_conversation(self):
        """Test handling photo in report conversation"""
        # Placeholder for photo handling test
        # In implementation, photos would be uploaded to Cloudinary
        pass


class TestTelegramLinkEndpoint:
    """Tests for Telegram account linking endpoint"""

    def test_link_endpoint_requires_auth(self):
        """Test that linking endpoint requires JWT authentication"""
        # Placeholder - actual test would use TestClient
        pass

    def test_link_endpoint_accepts_chat_id(self):
        """Test linking endpoint accepts chat_id and updates user"""
        # Placeholder for endpoint test
        pass
