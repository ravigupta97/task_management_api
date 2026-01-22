
"""
Quick test to verify database connection and models work.
Run with: python test_db_connection.py
"""

import asyncio
from app.database import AsyncSessionLocal, engine
from app.models import User, Task, Category, TaskStatus, TaskPriority
from app.core.security import get_password_hash


async def test_database_connection():
    """Test database connection and basic CRUD operations."""
    
    print("🔍 Testing database connection...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Test 1: Create a user
            print("\n✅ Test 1: Creating user...")
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password=get_password_hash("testpassword123"),
                full_name="Test User",
                is_active=True,
                is_verified=True
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"   User created: {test_user.username} (ID: {test_user.id})")
            
            # Test 2: Create a category
            print("\n✅ Test 2: Creating category...")
            test_category = Category(
                name="Work",
                color="#FF5733",
                user_id=test_user.id
            )
            session.add(test_category)
            await session.commit()
            await session.refresh(test_category)
            print(f"   Category created: {test_category.name} (ID: {test_category.id})")
            
            # Test 3: Create a task
            print("\n✅ Test 3: Creating task...")
            test_task = Task(
                title="Test Task",
                description="This is a test task to verify database connection",
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                user_id=test_user.id,
                category_id=test_category.id
            )
            session.add(test_task)
            await session.commit()
            await session.refresh(test_task)
            print(f"   Task created: {test_task.title} (ID: {test_task.id})")
            
            # Test 4: Query with relationships
            print("\n✅ Test 4: Querying with relationships...")
            from sqlalchemy import select
            
            result = await session.execute(
                select(User).where(User.username == "testuser")
            )
            user = result.scalar_one()
            print(f"   Found user: {user.username}")
            print(f"   User has {len(user.tasks)} task(s)")
            print(f"   User has {len(user.categories)} category(ies)")
            
            # Test 5: Cleanup
            print("\n✅ Test 5: Cleaning up...")
            await session.delete(test_task)
            await session.delete(test_category)
            await session.delete(test_user)
            await session.commit()
            print("   Test data deleted successfully")
            
            print("\n🎉 All database tests passed!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Close engine
    await engine.dispose()


# Note: get_password_hash needs to be implemented first
# For now, create a simple version in app/core/security.py
def setup_security_temp():
    """Temporary security setup for testing."""
    import os
    os.makedirs("app/core", exist_ok=True)
    
    with open("app/core/__init__.py", "w") as f:
        f.write("")
    
    with open("app/core/security.py", "w") as f:
        f.write("""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
""")


if __name__ == "__main__":
    # Setup temp security file
    setup_security_temp()
    
    # Run test
    asyncio.run(test_database_connection())