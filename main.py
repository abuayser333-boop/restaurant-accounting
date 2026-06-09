"""
main.py - نقطة الدخول الرئيسية
نظام محاسبة المطاعم
"""

import os
import sys

# إضافة مجلد المشروع لمسار البحث
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import initialize_database
from modules.invoices import InvoicesManager
from modules.expenses import ExpensesManager
from modules.inventory import InventoryManager
from modules.reports import ReportsManager


def print_header():
    """طباعة ترويسة البرنامج"""
    print("\n" + "="*50)
    print("       🍽️  نظام محاسبة المطاعم")
    print("         Restaurant Accounting System")
    print("              الإصدار 1.0.0")
    print("="*50)


def main_menu():
    """القائمة الرئيسية للبرنامج"""
    
    # تهيئة قاعدة البيانات عند أول تشغيل
    initialize_database()
    
    # إنشاء مديري الوحدات
    invoices_manager = InvoicesManager()
    expenses_manager = ExpensesManager()
    inventory_manager = InventoryManager()
    reports_manager = ReportsManager()
    
    while True:
        print_header()
        print("\n  الرجاء اختيار أحد الخيارات:")
        print("  " + "-"*35)
        print("  1. 📄 إدارة الفواتير (المبيعات)")
        print("  2. 💸 إدارة المصروفات")
        print("  3. 📦 إدارة المخزون")
        print("  4. 📊 التقارير المالية")
        print("  5. 🚪 الخروج")
        print("  " + "-"*35)
        
        choice = input("  اختر رقم القائمة (1-5): ").strip()
        
        if choice == "1":
            invoices_manager.run()
        elif choice == "2":
            expenses_manager.run()
        elif choice == "3":
            inventory_manager.run()
        elif choice == "4":
            reports_manager.run()
        elif choice == "5":
            print("\n  👋 شكراً لاستخدام نظام محاسبة المطاعم.")
            print("  جميع الحقوق محفوظة © 2024\n")
            sys.exit(0)
        else:
            print("\n  ❌ اختيار غير صحيح. الرجاء إدخال رقم من 1 إلى 5.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n  تم إيقاف البرنامج. مع السلامة! 👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ خطأ غير متوقع: {e}")
        sys.exit(1)
