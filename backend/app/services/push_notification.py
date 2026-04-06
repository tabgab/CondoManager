"""Push notification service using VAPID for Web Push."""
import json
import logging
from typing import Optional, Dict, Any, List

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Try to import pywebpush
try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    # Define a dummy WebPushException for testing
    class WebPushException(Exception):
        """Dummy WebPushException when pywebpush is not installed."""
        pass
    logger.warning("pywebpush not installed - push notifications disabled")

# Export WebPushException for tests and other modules
__all__ = ['PushNotificationService', 'push_service', 'WebPushException', 'WEBPUSH_AVAILABLE']


class PushNotificationService:
    """Service for sending Web Push notifications using VAPID."""
    
    def __init__(self):
        """Initialize push notification service with VAPID keys."""
        settings = get_settings()
        self.vapid_public_key = settings.VAPID_PUBLIC_KEY
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_claims_sub = settings.VAPID_CLAIMS_SUB
        self._subscriptions_cache: Dict[str, List[Dict]] = {}
    
    async def send_notification(
        self,
        subscription: Dict[str, str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        icon: str = "/icon-192x192.png",
        badge: str = "/badge-72x72.png",
        url: Optional[str] = None,
    ) -> bool:
        """
        Send push notification to a single subscription.
        
        Args:
            subscription: Dict with endpoint, p256dh, auth keys
            title: Notification title
            body: Notification body
            data: Custom data payload
            icon: Icon URL
            badge: Badge URL
            url: URL to open on click
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not WEBPUSH_AVAILABLE:
            logger.warning("pywebpush not available - cannot send notification")
            return False
        
        if not self.vapid_private_key:
            logger.warning("VAPID private key not configured - cannot send notification")
            return False
        
        endpoint = subscription.get("endpoint")
        p256dh = subscription.get("p256dh")
        auth = subscription.get("auth")
        
        if not all([endpoint, p256dh, auth]):
            logger.error("Invalid subscription data - missing required fields")
            return False
        
        # Build notification payload
        payload = {
            "title": title,
            "body": body,
            "icon": icon,
            "badge": badge,
        }
        
        if url:
            payload["url"] = url
        if data:
            payload["data"] = data
        
        subscription_info = {
            "endpoint": endpoint,
            "keys": {
                "p256dh": p256dh,
                "auth": auth,
            }
        }
        
        vapid_claims = {
            "sub": self.vapid_claims_sub,
        }
        
        try:
            response = webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=vapid_claims,
            )
            
            logger.info(f"Push notification sent to {endpoint[:50]}...")
            return True
            
        except WebPushException as e:
            logger.warning(f"WebPush failed for {endpoint[:50]}...: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending push notification: {e}")
            return False
    
    async def send_to_user(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Send notification to all devices of a user.
        
        Args:
            user_id: User ID to send to
            title: Notification title
            body: Notification body
            data: Custom data
            
        Returns:
            Number of successful sends
        """
        # Get subscriptions from cache or database
        subscriptions = self._subscriptions_cache.get(user_id, [])
        
        if not subscriptions:
            logger.debug(f"No push subscriptions for user {user_id}")
            return 0
        
        success_count = 0
        for sub in subscriptions:
            result = await self.send_notification(
                subscription=sub,
                title=title,
                body=body,
                data=data,
            )
            if result:
                success_count += 1
        
        return success_count
    
    async def send_to_users(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Send notification to multiple users.
        
        Args:
            user_ids: List of user IDs
            title: Notification title
            body: Notification body
            data: Custom data
            
        Returns:
            Dict with user_id -> success count
        """
        results = {}
        for user_id in user_ids:
            count = await self.send_to_user(user_id, title, body, data)
            results[user_id] = count
        return results
    
    async def broadcast_to_all(
        self,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Broadcast notification to all subscribed devices.
        
        Args:
            title: Notification title
            body: Notification body
            data: Custom data
            
        Returns:
            Total number of successful sends
        """
        total_success = 0
        for user_id, subscriptions in self._subscriptions_cache.items():
            for sub in subscriptions:
                result = await self.send_notification(
                    subscription=sub,
                    title=title,
                    body=body,
                    data=data,
                )
                if result:
                    total_success += 1
        
        return total_success
    
    def update_user_subscriptions(self, user_id: str, subscriptions: List[Dict]) -> None:
        """
        Update cached subscriptions for a user.
        
        Args:
            user_id: User ID
            subscriptions: List of subscription dicts
        """
        self._subscriptions_cache[user_id] = subscriptions
    
    def remove_user_subscriptions(self, user_id: str) -> None:
        """Remove cached subscriptions for a user."""
        if user_id in self._subscriptions_cache:
            del self._subscriptions_cache[user_id]


# Global service instance
push_service = PushNotificationService()
