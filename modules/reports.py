"""
modules/reports.py - وحدة التقارير المالية
نظام محاسبة المطاعم
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection


class ReportsManager:
    """مدير التقارير المالية"""

    def run(self):
        """تشغيل قائمة التقارير"""
        while True:
            print("\n" + "="*40)
            print("      📊 التقارير المالية")
            print("="*40)
            print("1. تقرير اليوم")
            print("2. تقرير الأسبوع الحالي")
            print("3. تقرير الشهر الحالي")
            print("4. تقرير فترة مخصصة")
            print("5. تقرير المصروفات حسب الفئة")
            print("6. أكثر الأصناف مبيعاً")
            print("7. الرجوع للقائمة الرئيسية")
            print("-"*40)
            choice = input("اختر: ").strip()

            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            
            if choice == "1":
                self.profit_loss_report(today, today, "تقرير اليوم")
            elif choice == "2":
                start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
                self.profit_loss_report(start, today, "تقرير الأسبوع الحالي")
            elif choice == "3":
                start = now.replace(day=1).strftime("%Y-%m-%d")
                self.profit_loss_report(start, today, "تقرير الشهر الحالي")
            elif choice == "4":
                date_from = input("من تاريخ (YYYY-MM-DD): ").strip()
                date_to = input("إلى تاريخ (YYYY-MM-DD): ").strip()
                self.profit_loss_report(date_from, date_to, f"تقرير من {date_from} إلى {date_to}")
            elif choice == "5":
                self.expenses_by_category_report()
            elif choice == "6":
                self.top_selling_items()
            elif choice == "7":
                break
            else:
                print("❌ اختيار غير صحيح.")

    def profit_loss_report(self, date_from: str, date_to: str, title: str = ""):
        """تقرير الأرباح والخسائر"""
        conn = get_connection()
        cursor = conn.cursor()

        # إجمالي المبيعات
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(subtotal), 0) as total_subtotal,
                COALESCE(SUM(tax_amount), 0) as total_tax,
                COALESCE(SUM(total_amount), 0) as total_revenue
            FROM invoices 
            WHERE status='مدفوعة' AND date BETWEEN ? AND ?
        """, (date_from, date_to))
        sales = cursor.fetchone()

        # إجمالي المصروفات
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(amount), 0) as total_expenses
            FROM expenses 
            WHERE date BETWEEN ? AND ?
        """, (date_from, date_to))
        expenses = cursor.fetchone()

        # المصروفات حسب الفئة
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        """, (date_from, date_to))
        expense_categories = cursor.fetchall()

        conn.close()

        total_revenue = sales['total_revenue'] or 0
        total_expenses = expenses['total_expenses'] or 0
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        print("\n" + "="*55)
        print(f"  📊 {title}")
        print(f"  الفترة: {date_from} ~ {date_to}")
        print("="*55)
        print(f"\n  💰 الإيرادات:")
        print(f"     عدد الفواتير:        {sales['count']:>10}")
        print(f"     المبيعات (قبل الضريبة): {sales['total_subtotal']:>10.2f} ريال")
        print(f"     ضريبة القيمة المضافة:  {sales['total_tax']:>10.2f} ريال")
        print(f"     إجمالي الإيرادات:    {total_revenue:>10.2f} ريال")
        
        print(f"\n  💸 المصروفات:")
        print(f"     عدد المصروفات:       {expenses['count']:>10}")
        for cat in expense_categories:
            print(f"     {cat['category']:<25} {cat['total']:>10.2f} ريال")
        print(f"     إجمالي المصروفات:    {total_expenses:>10.2f} ريال")
        
        print("\n" + "-"*55)
        profit_icon = "✅" if net_profit >= 0 else "❌"
        print(f"  {profit_icon} صافي الربح/الخسارة:    {net_profit:>10.2f} ريال")
        print(f"  📈 هامش الربح:          {profit_margin:>10.1f}%")
        print("="*55)

    def expenses_by_category_report(self):
        """تقرير المصروفات مصنفة"""
        now = datetime.now()
        first_day = now.replace(day=1).strftime("%Y-%m-%d")
        today = now.strftime("%Y-%m-%d")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        """, (first_day, today))
        rows = cursor.fetchall()
        
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?", (first_day, today))
        grand_total = cursor.fetchone()[0] or 0
        conn.close()

        if not rows:
            print("\n📭 لا توجد مصروفات هذا الشهر.")
            return

        print(f"\n{'='*55}")
        print(f"  تقرير المصروفات حسب الفئة - {now.strftime('%B %Y')}")
        print(f"  {'الفئة':<25} {'العدد':>6} {'الإجمالي':>10} {'%':>6}")
        print(f"  {'-'*50}")
        
        for row in rows:
            pct = (row['total'] / grand_total * 100) if grand_total > 0 else 0
            print(f"  {row['category']:<25} {row['count']:>6} {row['total']:>10.2f} {pct:>5.1f}%")
        
        print(f"  {'='*50}")
        print(f"  {'الإجمالي':<25} {sum(r['count'] for r in rows):>6} {grand_total:>10.2f}")

    def top_selling_items(self):
        """أكثر الأصناف مبيعاً"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT items FROM invoices WHERE status='مدفوعة'")
        rows = cursor.fetchall()
        conn.close()

        import json
        items_count = {}
        items_revenue = {}

        for row in rows:
            try:
                items = json.loads(row['items'])
                for item in items:
                    name = item.get('name', '')
                    qty = item.get('quantity', 0)
                    total = item.get('total', 0)
                    items_count[name] = items_count.get(name, 0) + qty
                    items_revenue[name] = items_revenue.get(name, 0) + total
            except Exception:
                continue

        if not items_count:
            print("\n📭 لا توجد بيانات مبيعات.")
            return

        sorted_items = sorted(items_revenue.items(), key=lambda x: x[1], reverse=True)[:10]

        print(f"\n{'='*55}")
        print(f"  🏆 أكثر 10 أصناف مبيعاً")
        print(f"  {'الصنف':<25} {'الكمية':>8} {'الإيرادات':>10}")
        print(f"  {'-'*50}")
        for i, (name, revenue) in enumerate(sorted_items, 1):
            qty = items_count.get(name, 0)
            print(f"  {i}. {name:<23} {qty:>8.1f} {revenue:>10.2f} ريال")
        print(f"  {'='*55}")
