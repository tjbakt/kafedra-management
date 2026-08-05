from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


BASE_DIR = Path(__file__).resolve().parent.parent

TEST_SETTINGS = "config.settings.test"

ENVIRONMENT = {
    **os.environ,
    "DJANGO_SETTINGS_MODULE": TEST_SETTINGS,
}


def run_command(
    title: str,
    command: Sequence[str],
) -> None:
    """
    Выполняет одну обязательную backend-проверку.

    При первой ошибке завершает весь процесс
    с тем же кодом возврата.
    """
    separator = "=" * 72

    print()
    print(separator)
    print(title)
    print(separator)
    print(" ".join(command))
    print()

    result = subprocess.run(
        list(command),
        cwd=BASE_DIR,
        env=ENVIRONMENT,
        check=False,
    )

    if result.returncode != 0:
        print()
        print(
            f"Проверка завершилась ошибкой: {title}",
            file=sys.stderr,
        )
        raise SystemExit(result.returncode)


def remove_old_coverage() -> None:
    coverage_file = BASE_DIR / ".coverage"
    coverage_xml = BASE_DIR / "coverage.xml"

    if coverage_file.exists():
        coverage_file.unlink()

    if coverage_xml.exists():
        coverage_xml.unlink()


def main() -> None:
    python = sys.executable

    run_command(
        "1. Проверка конфигурации Django",
        [
            python,
            "manage.py",
            "check",
            "--settings",
            TEST_SETTINGS,
        ],
    )

    run_command(
        "2. Проверка отсутствия новых миграций",
        [
            python,
            "manage.py",
            "makemigrations",
            "--check",
            "--dry-run",
            "--settings",
            TEST_SETTINGS,
        ],
    )

    run_command(
        "3. Проверка OpenAPI-схемы",
        [
            python,
            "manage.py",
            "spectacular",
            "--file",
            "openapi-schema.yml",
            "--validate",
            "--fail-on-warn",
            "--settings",
            TEST_SETTINGS,
        ],
    )

    remove_old_coverage()

    run_command(
        "4. Полный регрессионный набор тестов",
        [
            python,
            "-m",
            "coverage",
            "run",
            "manage.py",
            "test",
            "tests",
            "--settings",
            TEST_SETTINGS,
            "--verbosity",
            "2",
        ],
    )

    run_command(
        "5. Текстовый отчёт покрытия",
        [
            python,
            "-m",
            "coverage",
            "report",
            "--fail-under",
            "70",
        ],
    )

    run_command(
        "6. XML-отчёт покрытия",
        [
            python,
            "-m",
            "coverage",
            "xml",
        ],
    )

    run_command(
        "7. HTML-отчёт покрытия",
        [
            python,
            "-m",
            "coverage",
            "html",
        ],
    )

    print()
    print("=" * 72)
    print("Все backend-проверки успешно завершены.")
    print("=" * 72)
    print(
        f"Coverage XML: {BASE_DIR / 'coverage.xml'}"
    )
    print(
        f"Coverage HTML: "
        f"{BASE_DIR / 'htmlcov' / 'index.html'}"
    )


if __name__ == "__main__":
    main()