#!/usr/bin/env python3
"""
CondoManager Admin User Creation Script

Interactive script to create the first super_admin user after deployment.
Can be run from Render Shell, local terminal, or any environment with DB access.

Usage:
    python scripts/create_admin.py
    
Environment:
    DATABASE_URL must be set (or loaded from .env file)
"""

import asyncio
import getpass
import os
import re
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import get_db_session, engine
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.models.user import User


def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"


def check_admin_exists() -> bool:
    """Check if any super_admin already exists"""
    import asyncio
    
    async def _check():
        async with get_db_session() as db:
            result = await db.execute(
                select(User).where(User.role == "super_admin")
            )
            return result.scalar_one_or_none() is not None
    
    return asyncio.run(_check())


async def create_admin_user():
    """Interactive admin user creation"""
    
    print("=" * 60)
    print("CondoManager - Admin User Creation")
    print("=" * 60)
    print()
    
    # Check DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print()
        print("Please set it first:")
        print("  export DATABASE_URL=postgresql://...")
        print()
        sys.exit(1)
    
    # Mask password in display
    display_url = db_url.replace(
        "://", "://***:***@" if "://" in db_url else "://"
    )
    print(f"Database: {display_url}")
    print()
    
    # Check if admin already exists
    try:
        if check_admin_exists():
            print("⚠️  Warning: A super_admin user already exists!")
            response = input("Do you want to create another admin? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
    except Exception as e:
        print(f"⚠️  Could not check existing admins: {e}")
        print("Continuing anyway...")
        print()
    
    # Collect user input
    print("Enter admin user details:")
    print("-" * 40)
    
    # Email
    while True:
        email = input("Email: ").strip()
        if not email:
            print("❌ Email is required")
            continue
        if not validate_email(email):
            print("❌ Invalid email format")
            continue
        break
    
    # First name
    first_name = input("First Name: ").strip()
    if not first_name:
        first_name = "Admin"
    
    # Last name
    last_name = input("Last Name: ").strip()
    if not last_name:
        last_name = "User"
    
    # Phone (optional)
    phone = input("Phone (optional): ").strip()
    
    # Password
    print()
    print("Password requirements:")
    print("  - At least 8 characters")
    print("  - At least one uppercase letter (A-Z)")
    print("  - At least one lowercase letter (a-z)")
    print("  - At least one digit (0-9)")
    print("  - At least one special character (!@#$%^&*...)")
    print()
    
    while True:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm Password: ")
        
        if password != confirm:
            print("❌ Passwords don't match")
            continue
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            print(f"❌ {msg}")
            continue
        
        print(f"✓ {msg}")
        break
    
    # Confirm creation
    print()
    print("=" * 60)
    print("Review:")
    print(f"  Email: {email}")
    print(f"  Name: {first_name} {last_name}")
    print(f"  Phone: {phone or 'Not provided'}")
    print(f"  Role: super_admin")
    print()
    
    confirm = input("Create this admin user? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    # Create the user
    print()
    print("Creating admin user...")
    
    try:
        async with get_db_session() as db:
            user_data = UserCreate(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role="super_admin",
                phone=phone or None
            )
            
            user = await create_user(db, user_data)
            
            print()
            print("=" * 60)
            print("✅ Admin user created successfully!")
            print("=" * 60)
            print()
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.first_name} {user.last_name}")
            print(f"  Role: {user.role}")
            print()
            print("You can now log in at:")
            print("  Frontend: https://your-frontend.vercel.app")
            print()
            print("IMPORTANT: Store the password securely!")
            print("This password cannot be recovered.")
            print()
            
    except Exception as e:
        print()
        print("❌ Error creating admin user:")
        print(f"   {e}")
        print()
        sys.exit(1)


def quick_create():
    """Quick create with environment variables (for CI/automation)"""
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    
    if not email or not password:
        print("For quick create, set ADMIN_EMAIL and ADMIN_PASSWORD")
        sys.exit(1)
    
    async def _create():
        async with get_db_session() as db:
            user_data = UserCreate(
                email=email,
                password=password,
                first_name=os.getenv("ADMIN_FIRST_NAME", "Admin"),
                last_name=os.getenv("ADMIN_LAST_NAME", "User"),
                role="super_admin",
                phone=os.getenv("ADMIN_PHONE")
            )
            user = await create_user(db, user_data)
            print(f"Created admin: {user.email}")
    
    asyncio.run(_create())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_create()
    else:
        asyncio.run(create_admin_user())
