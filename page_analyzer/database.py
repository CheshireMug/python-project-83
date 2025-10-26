import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Создаёт и возвращает подключение к базе данных."""
    return psycopg2.connect(DATABASE_URL)


def get_all_urls():
    """Возвращает все URL с датой последней проверки и статусом."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT
                    urls.id,
                    urls.name,
                    urls.created_at,
                    MAX(url_checks.created_at) AS last_check
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                GROUP BY urls.id, urls.name, urls.created_at
                ORDER BY urls.id DESC;
            """)
            return cur.fetchall()


def get_url_by_name(name):
    """Возвращает запись по имени сайта (если есть)."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s;", (name,))
            return cur.fetchone()


def get_url_by_id(url_id):
    """Возвращает запись по ID."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s;", (url_id,))
            return cur.fetchone()


def insert_url(name):
    """Добавляет новый URL и возвращает его ID."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at) \
VALUES (%s, %s) RETURNING id;",
                (name, datetime.utcnow().date())
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id


def get_last_check(url_id):
    """Возвращает последнюю проверку для заданного URL."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT 1;
            """, (url_id,))
            return cur.fetchone()


def get_checks_by_url_id(url_id):
    """Возвращает все проверки конкретного URL (по убыванию id)."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;
            """, (url_id,))
            return cur.fetchall()


def insert_check(url_id, h1, title, description, status_code):
    """Создаёт новую запись проверки для заданного URL."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code, \
                    h1, title, description, created_at) \
                 VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (
                    url_id, status_code, h1, title,
                    description, datetime.utcnow().date()
                    )
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
