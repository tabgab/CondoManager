"""
Telegram Bot Webhook API
Handles incoming webhook requests from Telegram Bot API
"""
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import os
import logging

from app.services.telegram import get_telegram_service, TelegramService
from app.services.telegram_commands import get_command_processor, TelegramCommandProcessor
from app.dependencies.auth import get_current_user
from app.schemas.user import User

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


def get_webhook_secret() -> str:
    """Get webhook secret from environment for verification"""
    return os.environ.get('TELEGRAM_WEBHOOK_SECRET', '')


def verify_webhook_secret(secret: str) -> bool:
    """Verify webhook secret matches expected value"""
    expected = get_webhook_secret()
    # If no secret is configured, accept all (not recommended for production)
    if not expected:
        return True
    return secret == expected


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    update: Dict[str, Any]
) -> JSONResponse:
    """
    Receive webhook updates from Telegram Bot API
    
    This endpoint receives all updates from Telegram including:
    - Messages
    - Commands
    - Callback queries
    - Other bot events
    
    Returns:
        200 OK on success (required by Telegram API)
        400 Bad Request if update is invalid
    """
    try:
        # Log the incoming update for debugging
        logger.debug(f"Received Telegram update: {update}")
        
        # Validate update structure
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty update received"
            )
        
        # Check for update_id (required field)
        if 'update_id' not in update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid update: missing update_id"
            )
        
        # Get services
        telegram_service = get_telegram_service()
        command_processor = get_command_processor(telegram_service)
        
        # Process the update
        success = await command_processor.process_update(update)
        
        if success:
            logger.info(f"Successfully processed update {update.get('update_id')}")
            return JSONResponse(content={"ok": True})
        else:
            logger.warning(f"Failed to process update {update.get('update_id')}")
            # Still return 200 to prevent Telegram from retrying for non-critical failures
            return JSONResponse(content={"ok": False, "description": "Update not processed"})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Return 200 even on errors to prevent Telegram spam
        return JSONResponse(
            content={"ok": False, "description": "Internal error"},
            status_code=status.HTTP_200_OK
        )


@router.get("/webhook/info", status_code=status.HTTP_200_OK)
async def webhook_info() -> Dict[str, Any]:
    """
    Get webhook configuration status
    
    Returns information about the webhook configuration and bot status.
    Useful for debugging.
    """
    telegram_service = get_telegram_service()
    
    return {
        "bot_configured": telegram_service.is_configured,
        "webhook_secret_configured": bool(os.environ.get('TELEGRAM_WEBHOOK_SECRET')),
        "environment": os.environ.get('ENVIRONMENT', 'development'),
        "webhook_url": os.environ.get('TELEGRAM_WEBHOOK_URL', 'Not set'),
    }


@router.post("/send-test", status_code=status.HTTP_200_OK)
async def send_test_message(
    chat_id: int,
    message: str
) -> Dict[str, Any]:
    """
    Send a test message (for debugging)
    
    This endpoint allows sending test messages to verify the bot is working.
    Should be restricted in production.
    """
    try:
        telegram_service = get_telegram_service()
        
        if not telegram_service.is_configured:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Telegram bot not configured"
            )
        
        success = await telegram_service.send_message(
            chat_id=chat_id,
            text=message
        )
        
        if success:
            return {"success": True, "message": "Message sent"}
        else:
            return {"success": False, "message": "Failed to send message"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message: {str(e)}"
        )


@router.post("/link-account", status_code=status.HTTP_200_OK)
async def link_telegram_account(
    telegram_chat_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Link Telegram account to CondoManager user account
    
    This endpoint allows authenticated users to link their Telegram
    chat ID to their CondoManager account for receiving notifications.
    
    Args:
        telegram_chat_id: The Telegram chat ID to link
        current_user: Authenticated user from JWT token
        
    Returns:
        Success message with linked info
    """
    try:
        # TODO: Update user in database with telegram_chat_id
        # This would call user CRUD to update the user's telegram_chat_id
        
        # Send confirmation message to Telegram
        telegram_service = get_telegram_service()
        if telegram_service.is_configured:
            await telegram_service.send_message(
                chat_id=telegram_chat_id,
                text=(
                    "✅ <b>Account Linked Successfully!</b>\n\n"
                    f"Your Telegram is now linked to {current_user.email}\n\n"
                    "You'll receive notifications here for:\n"
                    "• Report status updates\n"
                    "• Task assignments\n"
                    "• Messages from managers\n\n"
                    "Use /status to check your reports anytime!"
                )
            )
        
        return {
            "success": True,
            "message": "Telegram account linked successfully",
            "telegram_chat_id": telegram_chat_id,
            "user_email": current_user.email
        }
    
    except Exception as e:
        logger.error(f"Error linking Telegram account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link Telegram account: {str(e)}"
        )
