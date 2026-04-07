"""
Telegram Bot Service
Handles Telegram Bot API interactions
"""
import os
from typing import Optional
from telegram import Bot
from telegram.constants import ParseMode


class TelegramService:
    """Service for interacting with Telegram Bot API"""
    
    _instance: Optional['TelegramService'] = None
    _bot: Optional[Bot] = None
    
    def __new__(cls) -> 'TelegramService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
            
        self._token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if self._token:
            self._bot = Bot(token=self._token)
        self._initialized = True
    
    @property
    def bot(self) -> Optional[Bot]:
        """Get the bot instance"""
        return self._bot
    
    @property
    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return self._bot is not None
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = ParseMode.HTML,
        disable_web_page_preview: bool = True
    ) -> bool:
        """
        Send a message to a chat
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Message parse mode (HTML, Markdown, etc.)
            disable_web_page_preview: Whether to disable link previews
            
        Returns:
            True if message was sent successfully
        """
        if not self._bot:
            raise RuntimeError("Telegram bot not configured. Set TELEGRAM_BOT_TOKEN environment variable.")
        
        try:
            await self._bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_notification(
        self,
        chat_id: int,
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> bool:
        """
        Send a formatted notification message
        
        Args:
            chat_id: Telegram chat ID
            title: Notification title
            message: Notification message
            action_url: Optional URL to include
            
        Returns:
            True if message was sent successfully
        """
        text = f"<b>{title}</b>\n\n{message}"
        
        if action_url:
            text += f"\n\n<a href='{action_url}'>View Details</a>"
        
        return await self.send_message(chat_id=chat_id, text=text)
    
    async def send_welcome_message(self, chat_id: int, first_name: str) -> bool:
        """
        Send welcome message to new user
        
        Args:
            chat_id: Telegram chat ID
            first_name: User's first name
            
        Returns:
            True if message was sent successfully
        """
        text = (
            f"👋 Welcome to <b>CondoManager</b>, {first_name}!\n\n"
            "I'm your condominium management assistant. I can help you:\n\n"
            "📋 Submit and track maintenance reports\n"
            "🔔 Receive notifications about your requests\n"
            "📱 Get updates on tasks and assignments\n\n"
            "<b>Available commands:</b>\n"
            "/start - Show this welcome message\n"
            "/help - List all commands\n"
            "/link - Link your Telegram to your CondoManager account\n\n"
            "Need help? Contact your building manager."
        )
        
        return await self.send_message(chat_id=chat_id, text=text)
    
    async def send_help_message(self, chat_id: int) -> bool:
        """
        Send help message with available commands
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            True if message was sent successfully
        """
        text = (
            "<b>🤖 CondoManager Bot Commands</b>\n\n"
            "<b>General:</b>\n"
            "/start - Start the bot and see welcome message\n"
            "/help - Show this help message\n"
            "/link - Link your Telegram to your account\n\n"
            "<b>For Owners/Tenants:</b>\n"
            "/report - Submit a new maintenance report\n"
            "/status - Check status of your reports\n\n"
            "<b>For Managers:</b>\n"
            "/tasks - View pending tasks\n"
            "/reports - View pending reports\n\n"
            "<b>Need assistance?</b>\n"
            "Contact your building manager or use the web app."
        )
        
        return await self.send_message(chat_id=chat_id, text=text)


# Singleton instance
_telegram_service: Optional[TelegramService] = None


def get_telegram_service() -> TelegramService:
    """Get or create TelegramService singleton"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service
