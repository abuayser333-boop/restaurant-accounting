"""
database.py - إعداد قاعدة البيانات وإنشاء الجداول
نظام محاسبة المطاعم
"""

import sqlite3
import os

DB_NAME = "restaurant.db"


def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """إنشاء جداول قاعدة البيانات إذا لم تكن موجودة"""
    conn = get_connection()
    cursor = conn.cursor()

    # جدول الفواتير
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number  TEXT    NOT NULL UNIQUE,
            date            TEXT    NOT NULL,
            customer_name   TEXT    DEFAULT 'عميل نقدي',
            items           TEXT    NOT NULL,
            subtotal        REAL    NOT NULL DEFAULT 0,
            tax_rate        REAL    NOT NULL DEFAULT 0.15,
            tax_amount      REAL    NOT NULL DEFAULT 0,
            total_amount    REAL    NOT NULL,
            payment_method  TEXT    DEFAULT 'نقد',
            status          TEXT    DEFAULT 'مدفوعة',
            notes           TEXT    DEFAULT '',
            created_at      TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # جدول المصروفات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            payment_method TEXT DEFAULT 'نقد',
            notes       TEXT    DEFAULT '',
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # جدول المخزون
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name       TEXT    NOT NULL UNIQUE,
            category        TEXT    DEFAULT 'عام',
            quantity        REAL    NOT NULL DEFAULT 0,
            unit            TEXT    NOT NULL DEFAULT 'كجم',
            min_quantity    REAL    NOT NULL DEFAULT 1,
            cost_per_unit   REAL    NOT NULL DEFAULT 0,
            supplier        TEXT    DEFAULT '',
            last_updated    TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # جدول حركات المخزون
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id         INTEGER NOT NULL,
            transaction_type TEXT   NOT NULL,
            quantity        REAL    NOT NULL,
            notes           TEXT    DEFAULT '',
            created_at      TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (item_id) REFERENCES inventory(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ تم تهيئة قاعدة البيانات بنجاح.")


if __name__ == "__main__":
    initialize_database()
