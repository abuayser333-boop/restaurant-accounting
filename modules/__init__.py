"""
modules/__init__.py
وحدات نظام محاسبة المطاعم
"""

from .invoices import InvoicesManager
from .expenses import ExpensesManager
from .inventory import InventoryManager
from .reports import ReportsManager

__all__ = [
    "InvoicesManager",
    "ExpensesManager",
    "InventoryManager",
    "ReportsManager",
]
