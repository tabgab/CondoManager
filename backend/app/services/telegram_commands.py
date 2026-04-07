"""
Telegram Bot Command Processor
Handles incoming Telegram bot commands and conversations
"""
from typing import Dict, Any, Optional
from app.services.telegram import TelegramService
from app.services.telegram_conversations import (
    get_conversation_store,
    ConversationStore,
    ConversationState,
    get_category_name,
    get_category_display,
    get_priority_name,
    get_priority_display
)


class TelegramCommandProcessor:
    """Process Telegram bot commands and conversations"""
    
    def __init__(self, telegram_service: TelegramService):
        self.telegram_service = telegram_service
        self.conversation_store = get_conversation_store()
    
    async def process_update(self, update: Dict[str, Any]) -> bool:
        """
        Process an incoming Telegram update
        
        Args:
            update: Telegram Update object as dictionary
            
        Returns:
            True if update was processed successfully
        """
        # Check if this is a message update
        if 'message' not in update:
            return False
        
        message = update['message']
        
        # Check if message has text
        if 'text' not in message:
            # Handle photos if in conversation
            if 'photo' in message:
                return await self._handle_photo(message)
            return False
        
        # Extract info
        chat_id = message['chat']['id']
        text = message['text']
        user_info = message.get('from', {})
        
        # Check if user is in an active conversation
        if self.conversation_store.is_active(chat_id):
            return await self.handle_conversation_message(chat_id, text, user_info)
        
        # Parse command
        if text.startswith('/'):
            return await self._handle_command(chat_id, text, user_info)
        else:
            # Handle regular message
            return await self._handle_message(chat_id, text, user_info)
    
    async def _handle_command(
        self,
        chat_id: int,
        text: str,
        user_info: Dict[str, Any]
    ) -> bool:
        """Handle bot commands"""
        # Extract command (remove bot username if present)
        command = text.split()[0].split('@')[0].lower()
        
        if command == '/start':
            return await self.handle_start(chat_id, user_info)
        elif command == '/help':
            return await self.handle_help(chat_id)
        elif command == '/link':
            return await self.handle_link(chat_id, user_info)
        elif command == '/report':
            return await self.handle_report_start(chat_id, user_info)
        elif command == '/status':
            telegram_id = user_info.get('id')
            return await self.handle_status(chat_id, telegram_id)
        else:
            # Check if it's a report detail command like /report 123
            if command.startswith('/report'):
                parts = text.split()
                if len(parts) > 1:
                    report_id = parts[1]
                    return await self.handle_report_detail(chat_id, report_id)
            return await self.handle_unknown(chat_id, text)
    
    async def _handle_message(
        self,
        chat_id: int,
        text: str,
        user_info: Dict[str, Any]
    ) -> bool:
        """Handle regular (non-command) messages when not in conversation"""
        # Check if message looks like a report ID lookup (r-123 or R-123)
        text_stripped = text.strip()
        if text_stripped.lower().startswith('r-') or (text_stripped.isdigit() and len(text_stripped) < 10):
            return await self.handle_report_detail(chat_id, text_stripped)
        
        response = (
            "I received your message. To submit a report, type:\n\n"
            "📋 <b>/report</b> - Submit a new maintenance report\n"
            "📊 <b>/status</b> - Check your reports and tasks\n\n"
            "For help, type /help"
        )
        
        return await self.telegram_service.send_message(chat_id, response)
    
    async def handle_conversation_message(
        self,
        chat_id: int,
        text: str,
        user_info: Dict[str, Any]
    ) -> bool:
        """Handle messages during an active conversation"""
        state_data = self.conversation_store.get_state(chat_id)
        if not state_data:
            return await self._handle_message(chat_id, text, user_info)
        
        current_state = state_data['state']
        
        if current_state == ConversationState.AWAITING_TITLE:
            # User sent title, ask for category
            self.conversation_store.update_state(
                chat_id,
                ConversationState.AWAITING_CATEGORY,
                {'title': text}
            )
            
            category_text = (
                "📂 <b>Select Category</b>\n\n"
                "Please select a category by number:\n\n"
                "1️⃣ Maintenance\n"
                "2️⃣ Cleaning\n"
                "3️⃣ Safety\n"
                "4️⃣ Noise\n"
                "5️⃣ Other\n\n"
                "Reply with the number (1-5)"
            )
            return await self.telegram_service.send_message(chat_id, category_text)
        
        elif current_state == ConversationState.AWAITING_CATEGORY:
            # User sent category number
            if text not in ['1', '2', '3', '4', '5']:
                return await self.telegram_service.send_message(
                    chat_id,
                    "❌ Please reply with a number from 1 to 5"
                )
            
            category = get_category_name(text)
            self.conversation_store.update_state(
                chat_id,
                ConversationState.AWAITING_PRIORITY,
                {'category': category}
            )
            
            priority_text = (
                "⚡ <b>Select Priority</b>\n\n"
                "How urgent is this issue?\n\n"
                "🟢 1 - Low (not urgent)\n"
                "🔵 2 - Normal (standard)\n"
                "🟠 3 - High (needs attention)\n"
                "🔴 4 - Urgent (safety/critical)\n\n"
                "Reply with the number (1-4)"
            )
            return await self.telegram_service.send_message(chat_id, priority_text)
        
        elif current_state == ConversationState.AWAITING_PRIORITY:
            # User sent priority number
            if text not in ['1', '2', '3', '4']:
                return await self.telegram_service.send_message(
                    chat_id,
                    "❌ Please reply with a number from 1 to 4"
                )
            
            priority = get_priority_name(text)
            self.conversation_store.update_state(
                chat_id,
                ConversationState.AWAITING_DESCRIPTION,
                {'priority': priority}
            )
            
            desc_text = (
                "📝 <b>Issue Description</b>\n\n"
                "Please describe the issue in detail:\n\n"
                "• What happened?\n"
                "• Where is it located?\n"
                "• When did it start?\n\n"
                "Type your description now:"
            )
            return await self.telegram_service.send_message(chat_id, desc_text)
        
        elif current_state == ConversationState.AWAITING_DESCRIPTION:
            # User sent description, show summary
            self.conversation_store.update_state(
                chat_id,
                ConversationState.AWAITING_CONFIRMATION,
                {'description': text}
            )
            
            state_data = self.conversation_store.get_state(chat_id)
            data = state_data['data']
            
            summary = (
                "📋 <b>Report Summary</b>\n\n"
                f"<b>Title:</b> {data.get('title', 'N/A')}\n"
                f"<b>Category:</b> {get_category_display(text)}\n"
                f"<b>Priority:</b> {get_priority_display(text)}\n\n"
                f"<b>Description:</b>\n{data.get('description', 'N/A')[:200]}...\n\n"
                "✅ Reply <b>'yes'</b> to submit this report\n"
                "❌ Reply <b>'cancel'</b> to discard"
            )
            return await self.telegram_service.send_message(chat_id, summary)
        
        elif current_state == ConversationState.AWAITING_CONFIRMATION:
            # User confirmed or cancelled
            if text.lower() == 'yes':
                # Submit report
                state_data = self.conversation_store.get_state(chat_id)
                data = state_data['data']
                
                # TODO: Actually create report in database
                # For now, just confirm
                report_id = "R-" + str(chat_id)[-6:]  # Temporary ID
                
                confirm_text = (
                    "✅ <b>Report Submitted Successfully!</b>\n\n"
                    f"<b>Report ID:</b> {report_id}\n\n"
                    "Your report has been sent to the building manager. "
                    "You will receive updates here when the status changes.\n\n"
                    "Use /status to check your reports anytime."
                )
                
                self.conversation_store.end_conversation(chat_id)
                return await self.telegram_service.send_message(chat_id, confirm_text)
            
            elif text.lower() == 'cancel':
                self.conversation_store.end_conversation(chat_id)
                return await self.telegram_service.send_message(
                    chat_id,
                    "❌ Report cancelled. Your information has been discarded.\n\n"
                    "Type /report to start a new report."
                )
            else:
                return await self.telegram_service.send_message(
                    chat_id,
                    "Please reply with <b>'yes'</b> to submit or <b>'cancel'</b> to discard."
                )
        
        return True
    
    async def _handle_photo(self, message: Dict[str, Any]) -> bool:
        """Handle photo uploads during conversation"""
        chat_id = message['chat']['id']
        
        if not self.conversation_store.is_active(chat_id):
            return await self.telegram_service.send_message(
                chat_id,
                "📷 Photos can only be attached when submitting a report.\n\n"
                "Type /report to start."
            )
        
        # TODO: Download and upload to Cloudinary
        # For now, just acknowledge
        return await self.telegram_service.send_message(
            chat_id,
            "📷 Photo received! You can attach more photos or continue with your report."
        )
    
    async def handle_start(
        self,
        chat_id: int,
        user_info: Dict[str, Any]
    ) -> bool:
        """Handle /start command - Welcome message"""
        first_name = user_info.get('first_name', 'there')
        return await self.telegram_service.send_welcome_message(chat_id, first_name)
    
    async def handle_help(self, chat_id: int) -> bool:
        """Handle /help command - List available commands"""
        text = (
            "<b>🤖 CondoManager Bot Commands</b>\n\n"
            "<b>General:</b>\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/link - Link your Telegram to your account\n\n"
            "<b>For Owners/Tenants:</b>\n"
            "/report - Submit a new maintenance report\n"
            "/status - Check status of your reports\n\n"
            "<b>For Managers:</b>\n"
            "Access the web app for full management features.\n\n"
            "<b>Need assistance?</b>\n"
            "Contact your building manager."
        )
        return await self.telegram_service.send_message(chat_id, text)
    
    async def handle_link(
        self,
        chat_id: int,
        user_info: Dict[str, Any]
    ) -> bool:
        """Handle /link command - Link Telegram to CondoManager account"""
        telegram_user_id = user_info.get('id')
        username = user_info.get('username', 'N/A')
        
        text = (
            "🔗 <b>Link Your Account</b>\n\n"
            f"Telegram ID: <code>{telegram_user_id}</code>\n"
            f"Username: @{username}\n\n"
            "To link your Telegram to your CondoManager account:\n\n"
            "1. Log in to the web app\n"
            "2. Go to Settings → Notifications\n"
            "3. Enter your Telegram ID shown above\n\n"
            "Once linked, you'll receive notifications here!"
        )
        
        return await self.telegram_service.send_message(chat_id, text)
    
    async def handle_report_start(
        self,
        chat_id: int,
        user_info: Dict[str, Any]
    ) -> bool:
        """
        Handle /report command - Start report submission flow
        
        Args:
            chat_id: Telegram chat ID
            user_info: User info from Telegram
            
        Returns:
            True if message was sent successfully
        """
        # Check if already in conversation
        if self.conversation_store.is_active(chat_id):
            return await self.telegram_service.send_message(
                chat_id,
                "⚠️ You already have a report in progress.\n\n"
                "Continue where you left off or type 'cancel' to start over."
            )
        
        # Start new conversation
        self.conversation_store.start_conversation(chat_id, user_info.get('id'))
        
        first_name = user_info.get('first_name', 'there')
        
        text = (
            f"👋 Hi {first_name}! Let's submit a maintenance report.\n\n"
            "📝 <b>Step 1 of 5:</b> Issue Title\n\n"
            "Please provide a short, clear title for the issue:\n\n"
            "<i>Examples:</i>\n"
            "• Kitchen sink leaking\n"
            "• Broken light in hallway\n"
            "• AC not working\n\n"
            "Type your title now:"
        )
        
        return await self.telegram_service.send_message(chat_id, text)
    
    async def handle_status(
        self,
        chat_id: int,
        telegram_user_id: Optional[int]
    ) -> bool:
        """
        Handle /status command - Show user's reports and tasks
        
        Args:
            chat_id: Telegram chat ID
            telegram_user_id: Telegram user ID (None if not linked)
            
        Returns:
            True if message sent successfully
        """
        # Check if user is linked
        user = await self.get_or_create_user_by_telegram(chat_id)
        
        if not user:
            text = (
                "📊 <b>Your Status</b>\n\n"
                "⚠️ Your Telegram account is not linked to CondoManager.\n\n"
                "To see your reports and tasks:\n"
                "1. Log in to the web app\n"
                "2. Go to Settings → Notifications\n"
                "3. Link your Telegram account\n\n"
                "Or type /link for instructions."
            )
            return await self.telegram_service.send_message(chat_id, text)
        
        # TODO: Fetch actual reports and tasks from database
        # For now, show placeholder with instructions
        text = (
            "📊 <b>Your Status</b>\n\n"
            "📝 <b>Reports:</b>\n"
            "  • No active reports\n"
            "  • Type /report to submit a new issue\n\n"
            "📋 <b>Tasks:</b>\n"
            "  • No assigned tasks\n\n"
            "<i>Your reports and tasks will appear here once you have some.</i>\n\n"
            "Type /report to submit a maintenance request."
        )
        
        return await self.telegram_service.send_message(chat_id, text)
    
    async def handle_report_detail(
        self,
        chat_id: int,
        report_id: str
    ) -> bool:
        """
        Handle report detail request by ID
        
        Args:
            chat_id: Telegram chat ID
            report_id: Report ID (e.g., 'r-123' or '123')
            
        Returns:
            True if message sent successfully
        """
        # Parse report ID (remove 'r-' prefix if present)
        clean_id = report_id.lower().replace('r-', '').strip()
        
        if not clean_id.isdigit():
            return await self.telegram_service.send_message(
                chat_id,
                "❌ Invalid report ID format.\n\n"
                "Use: <code>r-123</code> or just <code>123</code>"
            )
        
        # TODO: Fetch actual report from database
        # For now, show placeholder
        text = (
            f"📋 <b>Report Details</b>\n\n"
            f"Report ID: <code>R-{clean_id}</code>\n\n"
            "Status: 🟡 Pending\n"
            "Title: Sample Report\n"
            "Category: Maintenance\n"
            "Priority: Normal\n\n"
            "Description:\n"
            "Sample description of the reported issue...\n\n"
            "<i>To see your actual reports, link your account first.</i>\n"
            "Type /link for instructions."
        )
        
        return await self.telegram_service.send_message(chat_id, text)
    
    async def handle_report_status(
        self,
        chat_id: int,
        user_telegram_id: int
    ) -> bool:
        """Handle /status command - Check report status"""
        # TODO: Look up user by telegram_chat_id and fetch reports
        
        text = (
            "📊 <b>Your Report Status</b>\n\n"
            "This feature requires linking your Telegram first.\n\n"
            "Use /link to get started, then link your account in the web app!"
        )
        
        return await self.telegram_service.send_message(chat_id, text)
    
    async def handle_unknown(self, chat_id: int, command: str) -> bool:
        """Handle unknown commands"""
        text = (
            f"❓ I don't understand: <code>{command}</code>\n\n"
            "Available commands:\n"
            "/start, /help, /link, /report, /status"
        )
        
        return await self.telegram_service.send_message(chat_id, text)
    
    async def get_or_create_user_by_telegram(
        self,
        telegram_chat_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get or create user by Telegram chat ID
        
        Args:
            telegram_chat_id: Telegram chat ID
            
        Returns:
            User dict if found/created, None otherwise
        """
        # TODO: Implement actual database lookup
        # This would call user CRUD to find by telegram_chat_id
        # For now, return None to indicate not linked
        return None


# Singleton instance
_command_processor: Optional[TelegramCommandProcessor] = None


def get_command_processor(telegram_service: Optional[TelegramService] = None) -> TelegramCommandProcessor:
    """Get or create TelegramCommandProcessor singleton"""
    global _command_processor
    if _command_processor is None:
        if telegram_service is None:
            telegram_service = TelegramService()
        _command_processor = TelegramCommandProcessor(telegram_service)
    return _command_processor
