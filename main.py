"""
main.py - نقطة الدخول الرئيسية
نظام محاسبة المطاعم
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import initialize_database
from modules.invoices     import InvoicesManager
from modules.expenses     import ExpensesManager
from modules.inventory    import InventoryManager
from modules.reports      import ReportsManager
from modules.breakeven    import BreakEvenManager
from modules.depreciation import DepreciationManager


def print_header():
    print("\n" + "="*52)
    print("       🍽️  نظام محاسبة المطاعم")
    print("         Restaurant Accounting System")
    print("              الإصدار 1.1.0")
    print("="*52)


def main_menu():
    initialize_database()

    invoices_mgr    = InvoicesManager()
    expenses_mgr    = ExpensesManager()
    inventory_mgr   = InventoryManager()
    reports_mgr     = ReportsManager()
    breakeven_mgr   = BreakEvenManager()
    depreciation_mgr = DepreciationManager()

    while True:
        print_header()
        print("\n  الرجاء اختيار أحد الخيارات:")
        print("  " + "-"*40)
        print("  1. 📄 إدارة الفواتير (المبيعات)")
        print("  2. 💸 إدارة المصروفات")
        print("  3. 📦 إدارة المخزون")
        print("  4. 📊 التقارير المالية")
        print("  5. ⚖️  نقطة التعادل (Break-Even)")
        print("  6. 📉 الاستهلاك - الرسبي (Depreciation)")
        print("  7. 🚪 الخروج")
        print("  " + "-"*40)

        choice = input("  اختر رقم القائمة (1-7): ").strip()

        if choice == "1":
            invoices_mgr.run()
        elif choice == "2":
            expenses_mgr.run()
        elif choice == "3":
            inventory_mgr.run()
        elif choice == "4":
            reports_mgr.run()
        elif choice == "5":
            breakeven_mgr.run()
        elif choice == "6":
            depreciation_mgr.run()
        elif choice == "7":
            print("\n  👋 شكراً لاستخدام نظام محاسبة المطاعم.")
            print("  جميع الحقوق محفوظة © 2024\n")
            sys.exit(0)
        else:
            print("\n  ❌ اختيار غير صحيح. الرجاء إدخال رقم من 1 إلى 7.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n  تم إيقاف البرنامج. مع السلامة! 👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ خطأ غير متوقع: {e}")
        sys.exit(1)
