"""
modules/inventory.py - وحدة إدارة المخزون
نظام محاسبة المطاعم
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection
from models import InventoryItem


class InventoryManager:
    """مدير المخزون - يوفر جميع عمليات إدارة المخزون"""

    def run(self):
        """تشغيل قائمة إدارة المخزون"""
        while True:
            print("\n" + "="*40)
            print("      📦 إدارة المخزون")
            print("="*40)
            print("1. إضافة مادة جديدة")
            print("2. عرض جميع المواد")
            print("3. تحديث الكمية (إضافة مشتريات)")
            print("4. خصم كمية (استهلاك)")
            print("5. المواد ذات المخزون المنخفض")
            print("6. حذف مادة")
            print("7. الرجوع للقائمة الرئيسية")
            print("-"*40)
            choice = input("اختر: ").strip()

            if choice == "1":
                self.add_item()
            elif choice == "2":
                self.list_items()
            elif choice == "3":
                self.update_quantity("إضافة")
            elif choice == "4":
                self.update_quantity("خصم")
            elif choice == "5":
                self.low_stock_alert()
            elif choice == "6":
                self.delete_item()
            elif choice == "7":
                break
            else:
                print("❌ اختيار غير صحيح.")

    def add_item(self):
        """إضافة مادة جديدة للمخزون"""
        print("\n--- إضافة مادة جديدة ---")
        
        item_name = input("اسم المادة: ").strip()
        if not item_name:
            print("❌ اسم المادة مطلوب.")
            return

        category = input("التصنيف (مثال: خضروات، لحوم، مشروبات): ").strip() or "عام"
        unit = input("وحدة القياس (كجم/لتر/علبة/حبة): ").strip() or "كجم"
        
        try:
            quantity = float(input("الكمية الابتدائية: "))
            min_quantity = float(input("الحد الأدنى للتنبيه: "))
            cost_per_unit = float(input("تكلفة الوحدة (ريال): "))
        except ValueError:
            print("❌ قيم غير صحيحة.")
            return

        supplier = input("المورد (اختياري): ").strip()

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO inventory (item_name, category, quantity, unit, min_quantity, cost_per_unit, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_name, category, quantity, unit, min_quantity, cost_per_unit, supplier))
            
            # تسجيل حركة المخزون
            item_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO inventory_transactions (item_id, transaction_type, quantity, notes)
                VALUES (?, ?, ?, ?)
            """, (item_id, "إضافة أولية", quantity, "إضافة المادة للنظام"))
            
            conn.commit()
            print(f"\n✅ تم إضافة: {item_name} | {quantity} {unit} | {cost_per_unit:.2f} ريال/{unit}")
        except Exception as e:
            print(f"❌ خطأ: {e} (ربما المادة موجودة بالفعل)")
        finally:
            conn.close()

    def list_items(self):
        """عرض جميع مواد المخزون"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY category, item_name")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n📭 المخزون فارغ.")
            return

        print("\n" + "="*75)
        print(f"  {'#':<4} {'الاسم':<20} {'التصنيف':<12} {'الكمية':>8} {'الوحدة':<6} {'الحد الأدنى':>10} {'الحالة':<10}")
        print("-"*75)
        
        total_value = 0
        for row in rows:
            status = "⚠️ منخفض" if row['quantity'] <= row['min_quantity'] else "✅ كافٍ"
            value = row['quantity'] * row['cost_per_unit']
            total_value += value
            print(f"  {row['id']:<4} {row['item_name']:<20} {row['category']:<12} {row['quantity']:>8.2f} {row['unit']:<6} {row['min_quantity']:>10.2f} {status:<10}")
        
        print("="*75)
        print(f"  إجمالي قيمة المخزون: {total_value:.2f} ريال | عدد الأصناف: {len(rows)}")

    def update_quantity(self, operation: str):
        """تحديث كمية مادة في المخزون"""
        self.list_items()
        try:
            item_id = int(input(f"\nأدخل رقم المادة ({operation}): "))
            quantity = float(input(f"الكمية ({operation}): "))
            notes = input("ملاحظات: ").strip()
        except ValueError:
            print("❌ قيم غير صحيحة.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"❌ لم يتم العثور على المادة #{item_id}")
            conn.close()
            return

        if operation == "خصم" and row['quantity'] < quantity:
            print(f"❌ الكمية المتاحة ({row['quantity']}) أقل من المطلوب ({quantity})")
            conn.close()
            return

        new_quantity = row['quantity'] + quantity if operation == "إضافة" else row['quantity'] - quantity
        
        cursor.execute(
            "UPDATE inventory SET quantity = ?, last_updated = datetime('now','localtime') WHERE id = ?",
            (new_quantity, item_id)
        )
        cursor.execute("""
            INSERT INTO inventory_transactions (item_id, transaction_type, quantity, notes)
            VALUES (?, ?, ?, ?)
        """, (item_id, operation, quantity, notes))
        
        conn.commit()
        conn.close()
        print(f"✅ {operation}: {row['item_name']} | الكمية الجديدة: {new_quantity:.2f} {row['unit']}")

    def low_stock_alert(self):
        """عرض المواد ذات المخزون المنخفض"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM inventory 
            WHERE quantity <= min_quantity 
            ORDER BY (quantity - min_quantity)
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n✅ جميع مواد المخزون بمستويات كافية.")
            return

        print(f"\n⚠️ تنبيه: {len(rows)} مادة تحتاج لإعادة تزويد:")
        print("-"*60)
        for row in rows:
            deficit = row['min_quantity'] - row['quantity']
            print(f"  ⚠️ {row['item_name']:<20} | متاح: {row['quantity']:.2f} {row['unit']} | ينقص: {deficit:.2f}")

    def delete_item(self):
        """حذف مادة من المخزون"""
        try:
            item_id = int(input("أدخل رقم المادة للحذف: ").strip())
        except ValueError:
            print("❌ رقم غير صحيح.")
            return

        confirm = input(f"⚠️ هل أنت متأكد من حذف المادة #{item_id}? (نعم/لا): ").strip()
        if confirm != "نعم":
            print("تم إلغاء الحذف.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        if cursor.rowcount > 0:
            print(f"✅ تم حذف المادة #{item_id} بنجاح.")
        else:
            print(f"❌ لم يتم العثور على المادة #{item_id}")
        conn.commit()
        conn.close()

    def get_inventory_value(self) -> float:
        """الحصول على إجمالي قيمة المخزون"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity * cost_per_unit) FROM inventory")
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0
