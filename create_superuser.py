import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a superuser/admin in the IoT API database")
    parser.add_argument("--name", required=True, help="User display name")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", required=True, help="User password")
    parser.add_argument(
        "--role",
        choices=["superadmin", "admin", "user", "device"],
        default="admin",
        help="User role",
    )
    parser.add_argument(
        "--inactive",
        action="store_true",
        help="Create the user as inactive",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Database URL to use for the connection",
    )
    args = parser.parse_args()

    sys.path.insert(0, os.path.join(BASE_DIR, "iot_platform"))

    from app.core.config import Settings
    from app.core.security import hash_password
    from app.db.session import SessionLocal
    from app.models.user import User, UserRole
    from app.repositories.user_repository import UserRepository

    if args.database_url:
        database_url = args.database_url
    else:
        settings = Settings()
        database_url = settings.DATABASE_URL

    os.environ["DATABASE_URL"] = database_url

    session = SessionLocal()
    try:
        repo = UserRepository(session)
        existing = repo.get_by_email(args.email)
        role = UserRole(args.role)

        if existing:
            existing.name = args.name
            existing.password_hash = hash_password(args.password)
            existing.role = role
            if args.inactive:
                existing.is_active = False
            repo.update(existing)
            print(f"Updated existing user '{args.email}' with role '{args.role}'")
        else:
            user = User(
                name=args.name,
                email=args.email,
                password_hash=hash_password(args.password),
                role=role,
                is_active=not args.inactive,
            )
            repo.create(user)
            print(f"Created new user '{args.email}' with role '{args.role}'")
    finally:
        session.close()


if __name__ == "__main__":
    main()
