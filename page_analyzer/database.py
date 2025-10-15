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
    """Возвращает все URL из базы в порядке убывания id."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT id, name, \
created_at FROM urls ORDER BY id DESC;")
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
