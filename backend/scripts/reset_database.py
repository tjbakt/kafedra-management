import os
import sys
from pathlib import Path

import django
from django.conf import settings
from django.db import connection

# Корень backend (где лежит package config)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.development",
)

django.setup()


def main() -> None:
    db_name = settings.DATABASES["default"]["NAME"]

    print()
    print("=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    print(f"Database: {db_name}")
    print()

    answer = input(
        "Type RESET to completely erase the database: "
    ).strip()

    if answer != "RESET":
        print("Cancelled.")
        return

    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")

    print()
    print("Database schema has been completely reset.")


if __name__ == "__main__":
    main()