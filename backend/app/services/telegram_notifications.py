"""
Telegram Notification Service
Sends real-time notifications to users via Telegram Bot
"""
from typing import Optional, List, Dict, Any
from app.services.telegram import get_telegram_service, TelegramService
from app.schemas.report import ReportResponse
from app.schemas.task import TaskResponse
import logging

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    """Service for sending notifications to users via Telegram"""
    
    def __init__(self, telegram_service: Optional[TelegramService] = None):
        self.telegram_service = telegram_service or get_telegram_service()
    
    async def notify_user(
        self,
        telegram_chat_id: int,
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> bool:
        """
        Send a notification to a specific user
        
        Args:
            telegram_chat_id: User's Telegram chat ID
            title: Notification title
            message: Notification message
            action_url: Optional URL to include
            
        Returns:
            True if sent successfully
        """
        if not self.telegram_service.is_configured:
            logger.warning("Telegram service not configured, skipping notification")
            return False
        
        return await self.telegram_service.send_notification(
            chat_id=telegram_chat_id,
            title=title,
            message=message,
            action_url=action_url
        )
    
    async def notify_user_of_report_update(
        self,
        telegram_chat_id: int,
        report: ReportResponse,
        status_change: Optional[str] = None
    ) -> bool:
        """
        Notify user about report status update
        
        Args:
            telegram_chat_id: User's Telegram chat ID
            report: Report data
            status_change: Description of status change (optional)
            
        Returns:
            True if sent successfully
        """
        title = "📋 Report Update"
        
        status_emoji = {
            "pending": "🟡",
            "acknowledged": "🔵",
            "task_created": "🟣",
            "resolved": "🟢",
            "rejected": "🔴"
        }.get(report.status, "⚪")
        
        message = (
            f"<b>{report.title}</b>\n\n"
            f"Status: {status_emoji} {report.status.replace('_', ' ').title()}\n"
        )
        
        if status_change:
            message += f"Update: {status_change}\n\n"
        
        message += f"Report ID: <code>R-{str(report.id)[:6]}</code>"
        
        return await self.notify_user(
            telegram_chat_id=telegram_chat_id,
            title=title,
            message=message,
            action_url=f"/reports/{report.id}"
        )
    
    async def notify_user_of_task_assignment(
        self,
        telegram_chat_id: int,
        task: TaskResponse
    ) -> bool:
        """
        Notify employee about new task assignment
        
        Args:
            telegram_chat_id: Employee's Telegram chat ID
            task: Task data
            
        Returns:
            True if sent successfully
        """
        title = "📋 New Task Assigned"
        
        priority_emoji = {
            "low": "🟢",
            "normal": "🔵",
            "high": "🟠",
            "urgent": "🔴"
        }.get(task.priority, "⚪")
        
        message = (
            f"<b>{task.title}</b>\n\n"
            f"Priority: {priority_emoji} {task.priority.title()}\n"
            f"Due: {task.due_date.strftime('%b %d, %Y') if task.due_date else 'Not set'}\n\n"
            f"{task.description[:200]}..." if len(task.description) > 200 else task.description
        )
        
        return await self.notify_user(
            telegram_chat_id=telegram_chat_id,
            title=title,
            message=message,
            action_url=f"/tasks/{task.id}"
        )
    
    async def notify_user_of_task_update(
        self,
        telegram_chat_id: int,
        task: TaskResponse,
        update_text: str,
        updated_by: str
    ) -> bool:
        """
        Notify about task progress update
        
        Args:
            telegram_chat_id: User's Telegram chat ID
            task: Task data
            update_text: The update message
            updated_by: Who made the update
            
        Returns:
            True if sent successfully
        """
        title = "📋 Task Update"
        
        status_emoji = {
            "pending": "🟡",
            "in_progress": "🔵",
            "on_hold": "🟠",
            "completed": "🟢",
            "verified": "✅",
            "cancelled": "❌"
        }.get(task.status, "⚪")
        
        message = (
            f"<b>{task.title}</b>\n\n"
            f"Status: {status_emoji} {task.status.replace('_', ' ').title()}\n"
            f"Updated by: {updated_by}\n\n"
            f"📝 {update_text[:300]}{'...' if len(update_text) > 300 else ''}"
        )
        
        return await self.notify_user(
            telegram_chat_id=telegram_chat_id,
            title=title,
            message=message,
            action_url=f"/tasks/{task.id}"
        )
    
    async def notify_multiple_users(
        self,
        telegram_chat_ids: List[int],
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> Dict[int, bool]:
        """
        Send notification to multiple users
        
        Args:
            telegram_chat_ids: List of Telegram chat IDs
            title: Notification title
            message: Notification message
            action_url: Optional URL
            
        Returns:
            Dictionary mapping chat_id to success status
        """
        results = {}
        
        for chat_id in telegram_chat_ids:
            try:
                success = await self.notify_user(
                    telegram_chat_id=chat_id,
                    title=title,
                    message=message,
                    action_url=action_url
                )
                results[chat_id] = success
            except Exception as e:
                logger.error(f"Failed to notify user {chat_id}: {e}")
                results[chat_id] = False
        
        return results
    
    async def notify_report_acknowledged(
        self,
        telegram_chat_id: int,
        report: ReportResponse,
        manager_name: str
    ) -> bool:
        """Notify that report was acknowledged by manager"""
        return await self.notify_user_of_report_update(
            telegram_chat_id=telegram_chat_id,
            report=report,
            status_change=f"Acknowledged by {manager_name}"
        )
    
    async def notify_report_resolved(
        self,
        telegram_chat_id: int,
        report: ReportResponse,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Notify that report was resolved"""
        status_change = "Issue resolved!"
        if resolution_notes:
            status_change += f"\n\nNotes: {resolution_notes}"
        
        return await self.notify_user_of_report_update(
            telegram_chat_id=telegram_chat_id,
            report=report,
            status_change=status_change
        )
    
    async def notify_task_completed(
        self,
        telegram_chat_id: int,
        task: TaskResponse,
        completed_by: str
    ) -> bool:
        """Notify manager that task was completed"""
        return await self.notify_user_of_task_update(
            telegram_chat_id=telegram_chat_id,
            task=task,
            update_text=f"Task marked as completed by {completed_by}",
            updated_by=completed_by
        )


# Singleton instance
_notification_service: Optional[TelegramNotificationService] = None


def get_notification_service(
    telegram_service: Optional[TelegramService] = None
) -> TelegramNotificationService:
    """Get or create TelegramNotificationService singleton"""
    global _notification_service
    if _notification_service is None:
        _notification_service = TelegramNotificationService(telegram_service)
    return _notification_service


# Convenience functions for direct use
async def notify_user_of_report_update(
    telegram_chat_id: int,
    report: ReportResponse,
    status_change: Optional[str] = None
) -> bool:
    """Convenience function to notify user of report update"""
    service = get_notification_service()
    return await service.notify_user_of_report_update(
        telegram_chat_id=telegram_chat_id,
        report=report,
        status_change=status_change
    )


async def notify_user_of_task_assignment(
    telegram_chat_id: int,
    task: TaskResponse
) -> bool:
    """Convenience function to notify user of task assignment"""
    service = get_notification_service()
    return await service.notify_user_of_task_assignment(
        telegram_chat_id=telegram_chat_id,
        task=task
    )


async def notify_user_of_task_update(
    telegram_chat_id: int,
    task: TaskResponse,
    update_text: str,
    updated_by: str
) -> bool:
    """Convenience function to notify user of task update"""
    service = get_notification_service()
    return await service.notify_user_of_task_update(
        telegram_chat_id=telegram_chat_id,
        task=task,
        update_text=update_text,
        updated_by=updated_by
    )


async def notify_multiple_users(
    telegram_chat_ids: List[int],
    title: str,
    message: str,
    action_url: Optional[str] = None
) -> Dict[int, bool]:
    """Convenience function to notify multiple users"""
    service = get_notification_service()
    return await service.notify_multiple_users(
        telegram_chat_ids=telegram_chat_ids,
        title=title,
        message=message,
        action_url=action_url
    )
