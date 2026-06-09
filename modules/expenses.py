"""
modules/expenses.py - وحدة إدارة المصروفات
نظام محاسبة المطاعم
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection
from models import Expense


class ExpensesManager:
    """مدير المصروفات - يوفر جميع عمليات المصروفات"""

    def run(self):
        """تشغيل قائمة إدارة المصروفات"""
        while True:
            print("\n" + "="*40)
            print("      💸 إدارة المصروفات")
            print("="*40)
            print("1. تسجيل مصروف جديد")
            print("2. عرض جميع المصروفات")
            print("3. مصروفات اليوم")
            print("4. مصروفات الشهر الحالي")
            print("5. حذف مصروف")
            print("6. الرجوع للقائمة الرئيسية")
            print("-"*40)
            choice = input("اختر: ").strip()

            if choice == "1":
                self.add_expense()
            elif choice == "2":
                self.list_expenses()
            elif choice == "3":
                today = datetime.now().strftime("%Y-%m-%d")
                self.list_expenses(date_from=today, date_to=today)
            elif choice == "4":
                now = datetime.now()
                first_day = now.replace(day=1).strftime("%Y-%m-%d")
                today = now.strftime("%Y-%m-%d")
                self.list_expenses(date_from=first_day, date_to=today)
            elif choice == "5":
                self.delete_expense()
            elif choice == "6":
                break
            else:
                print("❌ اختيار غير صحيح.")

    def add_expense(self):
        """تسجيل مصروف جديد"""
        print("\n--- تسجيل مصروف جديد ---")
        
        date = input(f"التاريخ (اتركه فارغاً لليوم {datetime.now().strftime('%Y-%m-%d')}): ").strip()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        print("\nالتصنيفات المتاحة:")
        for i, cat in enumerate(Expense.CATEGORIES, 1):
            print(f"  {i}. {cat}")
        
        cat_choice = input("اختر التصنيف (1-10): ").strip()
        try:
            category = Expense.CATEGORIES[int(cat_choice)-1]
        except (ValueError, IndexError):
            category = input("أدخل التصنيف يدوياً: ").strip()

        description = input("وصف المصروف: ").strip()
        if not description:
            print("❌ الوصف مطلوب.")
            return

        try:
            amount = float(input("المبلغ (ريال): "))
            if amount <= 0:
                print("❌ المبلغ يجب أن يكون أكبر من صفر.")
                return
        except ValueError:
            print("❌ قيمة غير صحيحة.")
            return

        payment_methods = ["نقد", "بطاقة", "تحويل"]
        print("\nطريقة الدفع:")
        for i, m in enumerate(payment_methods, 1):
            print(f"  {i}. {m}")
        pm_choice = input("اختر (1-3، افتراضي: 1): ").strip()
        payment_method = payment_methods[int(pm_choice)-1] if pm_choice in ("1","2","3") else "نقد"

        notes = input("ملاحظات (اختياري): ").strip()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (date, category, description, amount, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, category, description, amount, payment_method, notes))
        conn.commit()
        conn.close()

        print(f"\n✅ تم تسجيل المصروف: {category} - {description} - {amount:.2f} ريال")

    def list_expenses(self, date_from: str = None, date_to: str = None, limit: int = 30):
        """عرض قائمة المصروفات"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if date_from and date_to:
            cursor.execute("""
                SELECT * FROM expenses 
                WHERE date BETWEEN ? AND ? 
                ORDER BY date DESC LIMIT ?
            """, (date_from, date_to, limit))
            title = f"المصروفات من {date_from} إلى {date_to}"
        else:
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT ?", (limit,))
            title = "جميع المصروفات"
        
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print(f"\n📭 لا توجد مصروفات في هذه الفترة.")
            return

        print(f"\n{'='*65}")
        print(f"  {title}")
        print(f"  {'#':<4} {'التاريخ':<12} {'التصنيف':<15} {'الوصف':<20} {'المبلغ':>8}")
        print(f"  {'-'*60}")
        
        total = 0
        for row in rows:
            print(f"  {row['id']:<4} {row['date']:<12} {row['category']:<15} {row['description']:<20} {row['amount']:>8.2f}")
            total += row['amount']
        
        print(f"  {'='*60}")
        print(f"  {'الإجمالي':<52} {total:>8.2f}")
        print(f"  عدد السجلات: {len(rows)}")

    def delete_expense(self):
        """حذف مصروف"""
        try:
            expense_id = int(input("أدخل رقم المصروف للحذف: ").strip())
        except ValueError:
            print("❌ رقم غير صحيح.")
            return

        confirm = input(f"⚠️ هل أنت متأكد من حذف المصروف #{expense_id}? (نعم/لا): ").strip()
        if confirm != "نعم":
            print("تم إلغاء الحذف.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cursor.rowcount > 0:
            print(f"✅ تم حذف المصروف #{expense_id} بنجاح.")
        else:
            print(f"❌ لم يتم العثور على المصروف #{expense_id}")
        conn.commit()
        conn.close()

    def get_total_expenses(self, date_from: str = None, date_to: str = None) -> float:
        """الحصول على إجمالي المصروفات في فترة محددة"""
        conn = get_connection()
        cursor = conn.cursor()
        if date_from and date_to:
            cursor.execute(
                "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                (date_from, date_to)
            )
        else:
            cursor.execute("SELECT SUM(amount) FROM expenses")
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0

    def get_expenses_by_category(self, date_from: str = None, date_to: str = None) -> dict:
        """تجميع المصروفات حسب الفئة"""
        conn = get_connection()
        cursor = conn.cursor()
        if date_from and date_to:
            cursor.execute("""
                SELECT category, SUM(amount) as total 
                FROM expenses 
                WHERE date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
            """, (date_from, date_to))
        else:
            cursor.execute("""
                SELECT category, SUM(amount) as total 
                FROM expenses 
                GROUP BY category 
                ORDER BY total DESC
            """)
        rows = cursor.fetchall()
        conn.close()
        return {row['category']: row['total'] for row in rows}
