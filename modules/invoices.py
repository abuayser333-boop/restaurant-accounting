"""
modules/invoices.py - وحدة إدارة الفواتير
نظام محاسبة المطاعم
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection
from models import Invoice, InvoiceItem


class InvoicesManager:
    """مدير الفواتير - يوفر جميع عمليات الفواتير"""

    def run(self):
        """تشغيل قائمة إدارة الفواتير"""
        while True:
            print("\n" + "="*40)
            print("      📄 إدارة الفواتير")
            print("="*40)
            print("1. إنشاء فاتورة جديدة")
            print("2. عرض جميع الفواتير")
            print("3. عرض تفاصيل فاتورة")
            print("4. حذف فاتورة")
            print("5. الرجوع للقائمة الرئيسية")
            print("-"*40)
            choice = input("اختر: ").strip()

            if choice == "1":
                self.create_invoice()
            elif choice == "2":
                self.list_invoices()
            elif choice == "3":
                self.view_invoice()
            elif choice == "4":
                self.delete_invoice()
            elif choice == "5":
                break
            else:
                print("❌ اختيار غير صحيح.")

    def create_invoice(self):
        """إنشاء فاتورة جديدة"""
        print("\n--- إنشاء فاتورة جديدة ---")
        
        # توليد رقم فاتورة تلقائي
        date = datetime.now().strftime("%Y-%m-%d")
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        customer_name = input(f"اسم العميل (اتركه فارغاً لـ'عميل نقدي'): ").strip()
        if not customer_name:
            customer_name = "عميل نقدي"

        items = []
        print("\nأدخل الأصناف (اكتب 'انتهى' لإنهاء الإدخال):")
        while True:
            item_name = input("  اسم الصنف: ").strip()
            if item_name.lower() in ("انتهى", "done", ""):
                break
            try:
                qty = float(input("  الكمية: "))
                price = float(input("  سعر الوحدة: "))
                items.append(InvoiceItem(item_name, qty, price))
                print(f"  ✅ تم إضافة: {item_name} x{qty} = {qty*price:.2f} ريال")
            except ValueError:
                print("  ❌ قيمة غير صحيحة، حاول مرة أخرى.")

        if not items:
            print("❌ لا يمكن إنشاء فاتورة بدون أصناف.")
            return

        payment_methods = ["نقد", "بطاقة", "تحويل"]
        print("\nطريقة الدفع:")
        for i, m in enumerate(payment_methods, 1):
            print(f"  {i}. {m}")
        pm_choice = input("اختر (1-3، افتراضي: 1): ").strip()
        payment_method = payment_methods[int(pm_choice)-1] if pm_choice in ("1","2","3") else "نقد"

        invoice = Invoice(
            invoice_number=invoice_number,
            date=date,
            items=items,
            customer_name=customer_name,
            payment_method=payment_method
        )

        # حفظ في قاعدة البيانات
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices 
            (invoice_number, date, customer_name, items, subtotal, tax_rate, tax_amount, total_amount, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice.invoice_number, invoice.date, invoice.customer_name,
            invoice.items_to_json(), invoice.subtotal, invoice.tax_rate,
            invoice.tax_amount, invoice.total_amount, invoice.payment_method, invoice.status
        ))
        conn.commit()
        conn.close()

        invoice.display()
        print(f"\n✅ تم حفظ الفاتورة رقم: {invoice_number}")

    def list_invoices(self, limit: int = 20):
        """عرض قائمة الفواتير"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices ORDER BY date DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n📭 لا توجد فواتير مسجلة.")
            return

        print("\n" + "="*70)
        print(f"  {'رقم الفاتورة':<20} {'التاريخ':<12} {'العميل':<15} {'الإجمالي':>10} {'الحالة':<10}")
        print("-"*70)
        for row in rows:
            print(f"  {row['invoice_number']:<20} {row['date']:<12} {row['customer_name']:<15} {row['total_amount']:>10.2f} {row['status']:<10}")
        print("="*70)
        print(f"  إجمالي الفواتير المعروضة: {len(rows)}")

    def view_invoice(self):
        """عرض تفاصيل فاتورة محددة"""
        invoice_number = input("أدخل رقم الفاتورة: ").strip()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            print(f"❌ لم يتم العثور على الفاتورة: {invoice_number}")
            return

        items = Invoice.items_from_json(row["items"])
        invoice = Invoice(
            id=row["id"],
            invoice_number=row["invoice_number"],
            date=row["date"],
            customer_name=row["customer_name"],
            items=items,
            tax_rate=row["tax_rate"],
            payment_method=row["payment_method"],
            status=row["status"]
        )
        invoice.display()

    def delete_invoice(self):
        """حذف فاتورة"""
        invoice_number = input("أدخل رقم الفاتورة للحذف: ").strip()
        confirm = input(f"⚠️ هل أنت متأكد من حذف الفاتورة {invoice_number}? (نعم/لا): ").strip()
        
        if confirm != "نعم":
            print("تم إلغاء الحذف.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,))
        if cursor.rowcount > 0:
            print(f"✅ تم حذف الفاتورة {invoice_number} بنجاح.")
        else:
            print(f"❌ لم يتم العثور على الفاتورة: {invoice_number}")
        conn.commit()
        conn.close()

    def get_total_revenue(self, date_from: str = None, date_to: str = None) -> float:
        """الحصول على إجمالي الإيرادات في فترة محددة"""
        conn = get_connection()
        cursor = conn.cursor()
        if date_from and date_to:
            cursor.execute(
                "SELECT SUM(total_amount) FROM invoices WHERE status='مدفوعة' AND date BETWEEN ? AND ?",
                (date_from, date_to)
            )
        else:
            cursor.execute("SELECT SUM(total_amount) FROM invoices WHERE status='مدفوعة'")
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0
