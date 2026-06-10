"""
modules/__init__.py
وحدات نظام محاسبة المطاعم
"""

from .invoices     import InvoicesManager
from .expenses     import ExpensesManager
from .inventory    import InventoryManager
from .reports      import ReportsManager
from .breakeven    import BreakEvenManager
from .depreciation import DepreciationManager

__all__ = [
    "InvoicesManager",
    "ExpensesManager",
    "InventoryManager",
    "ReportsManager",
    "BreakEvenManager",
    "DepreciationManager",
]
