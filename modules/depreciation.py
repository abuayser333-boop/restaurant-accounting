"""
modules/depreciation.py - وحدة الاستهلاك (الرسبي)
نظام محاسبة المطاعم

الطرق المدعومة:
  1. القسط الثابت (Straight-Line)
  2. القسط المتناقص المزدوج (Double Declining Balance)
  3. مجموع أرقام السنوات (Sum of Years Digits - SYD)
  4. وحدات الإنتاج (Units of Production)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection


class DepreciationManager:
    """مدير الاستهلاك (الرسبي)"""

    def run(self):
        while True:
            print("\n" + "="*45)
            print("    📉 حساب الاستهلاك (الرسبي)")
            print("="*45)
            print("1. طريقة القسط الثابت")
            print("2. طريقة القسط المتناقص المزدوج")
            print("3. طريقة مجموع أرقام السنوات (SYD)")
            print("4. طريقة وحدات الإنتاج")
            print("5. مقارنة جميع الطرق")
            print("6. إدارة سجل الأصول الثابتة")
            print("7. تقرير الاستهلاك السنوي")
            print("8. الرجوع للقائمة الرئيسية")
            print("-"*45)
            choice = input("اختر: ").strip()
            if choice == "1":
                self.straight_line()
            elif choice == "2":
                self.declining_balance()
            elif choice == "3":
                self.sum_of_years()
            elif choice == "4":
                self.units_of_production()
            elif choice == "5":
                self.compare_methods()
            elif choice == "6":
                self.manage_assets()
            elif choice == "7":
                self.annual_depreciation_report()
            elif choice == "8":
                break
            else:
                print("❌ اختيار غير صحيح.")

    def _get_asset_inputs(self):
        """قراءة بيانات الأصل"""
        asset_name = input("  اسم الأصل (مثال: فرن، ثلاجة، مكيف): ").strip()
        try:
            cost          = float(input("  التكلفة الأصلية للأصل (ريال): "))
            salvage_value = float(input("  القيمة التخريدية عند انتهاء العمر (ريال) [0 إذا لا توجد]: "))
            useful_life   = int(input("  العمر الإنتاجي (سنوات): "))
        except ValueError:
            print("❌ قيم غير صحيحة.")
            return None
        if useful_life <= 0:
            print("❌ العمر الإنتاجي يجب أن يكون أكبر من صفر.")
            return None
        if cost < salvage_value:
            print("❌ القيمة التخريدية لا يمكن أن تتجاوز التكلفة الأصلية.")
            return None
        depreciable_cost = cost - salvage_value
        return asset_name, cost, salvage_value, useful_life, depreciable_cost

    def _print_header(self, asset_name, cost, salvage_value, useful_life, method):
        print("\n" + "="*62)
        print(f"  📉 جدول الاستهلاك - {method}")
        print("="*62)
        print(f"  الأصل:                   {asset_name}")
        print(f"  التكلفة الأصلية:         {cost:>14,.2f} ريال")
        print(f"  القيمة التخريدية:        {salvage_value:>14,.2f} ريال")
        print(f"  التكلفة القابلة للإهلاك: {cost-salvage_value:>13,.2f} ريال")
        print(f"  العمر الإنتاجي:          {useful_life:>10} سنوات")

    # ── 1. القسط الثابت ──────────────────────────────────────────
    def straight_line(self):
        print("\n--- 📏 طريقة القسط الثابت ---")
        print("الصيغة: الاستهلاك السنوي = (التكلفة - القيمة التخريدية) / العمر الإنتاجي\n")
        r = self._get_asset_inputs()
        if not r:
            return
        asset_name, cost, salvage_value, useful_life, dep_cost = r

        annual_dep = dep_cost / useful_life
        rate_pct   = (annual_dep / cost) * 100

        self._print_header(asset_name, cost, salvage_value, useful_life, "القسط الثابت")
        print(f"  معدل الاستهلاك:          {rate_pct:>13.2f}%")
        print(f"  قسط الاستهلاك السنوي:    {annual_dep:>13,.2f} ريال")
        print(f"  قسط الاستهلاك الشهري:    {annual_dep/12:>13,.2f} ريال")
        print("-"*62)
        print(f"  {'السنة':^6} {'الاستهلاك':>14} {'مجمع الاستهلاك':>16} {'القيمة الدفترية':>16}")
        print("-"*62)
        accumulated = 0
        for yr in range(1, useful_life + 1):
            accumulated += annual_dep
            bv           = cost - accumulated
            print(f"  {yr:^6} {annual_dep:>14,.2f} {accumulated:>16,.2f} {bv:>16,.2f}")
        print("="*62)

    # ── 2. القسط المتناقص المزدوج ────────────────────────────────
    def declining_balance(self):
        print("\n--- 📉 طريقة القسط المتناقص المزدوج ---")
        print("الصيغة: الاستهلاك = القيمة الدفترية × (2 / العمر الإنتاجي)\n")
        r = self._get_asset_inputs()
        if not r:
            return
        asset_name, cost, salvage_value, useful_life, dep_cost = r

        try:
            mult = float(input("  المضاعف (اضغط Enter للاستخدام القياسي ×2): ").strip() or "2")
        except ValueError:
            mult = 2.0

        rate = (1 / useful_life) * mult

        self._print_header(asset_name, cost, salvage_value, useful_life,
                           f"القسط المتناقص (×{mult})")
        print(f"  معدل الاستهلاك: {rate*100:.2f}% على القيمة الدفترية المتناقصة")
        print("-"*62)
        print(f"  {'السنة':^6} {'الاستهلاك':>14} {'مجمع الاستهلاك':>16} {'القيمة الدفترية':>16}")
        print("-"*62)

        bv  = cost
        acc = 0
        for yr in range(1, useful_life + 1):
            dep = bv * rate
            if bv - dep < salvage_value:
                dep = max(bv - salvage_value, 0)
            bv  -= dep
            acc += dep
            print(f"  {yr:^6} {dep:>14,.2f} {acc:>16,.2f} {bv:>16,.2f}")
            if bv <= salvage_value:
                break
        print("="*62)

    # ── 3. مجموع أرقام السنوات (SYD) ────────────────────────────
    def sum_of_years(self):
        print("\n--- 🔢 طريقة مجموع أرقام السنوات (SYD) ---")
        print("الصيغة: الاستهلاك = (السنوات المتبقية / مجموع الأرقام) × التكلفة القابلة للإهلاك\n")
        r = self._get_asset_inputs()
        if not r:
            return
        asset_name, cost, salvage_value, useful_life, dep_cost = r

        syd = useful_life * (useful_life + 1) / 2
        self._print_header(asset_name, cost, salvage_value, useful_life, "SYD - مجموع أرقام السنوات")
        print(f"  مجموع أرقام السنوات: {syd:.0f}")
        print("-"*62)
        print(f"  {'السنة':^6} {'النسبة':>8} {'الاستهلاك':>14} {'مجمع الاستهلاك':>14} {'القيمة الدفترية':>13}")
        print("-"*62)
        acc = 0
        for yr in range(1, useful_life + 1):
            remaining = useful_life - yr + 1
            frac      = remaining / syd
            dep       = frac * dep_cost
            acc      += dep
            bv        = cost - acc
            print(f"  {yr:^6} {frac*100:>7.1f}% {dep:>14,.2f} {acc:>14,.2f} {bv:>13,.2f}")
        print("="*62)

    # ── 4. وحدات الإنتاج ─────────────────────────────────────────
    def units_of_production(self):
        print("\n--- ⚙️ طريقة وحدات الإنتاج ---")
        print("مثال: معدات المطبخ يُقاس استهلاكها بعدد الوجبات المُنتجة\n")
        r = self._get_asset_inputs()
        if not r:
            return
        asset_name, cost, salvage_value, useful_life, dep_cost = r

        try:
            total_units = float(input("  إجمالي وحدات الإنتاج المتوقعة طوال العمر: "))
        except ValueError:
            print("❌ قيمة غير صحيحة.")
            return

        dep_per_unit = dep_cost / total_units
        self._print_header(asset_name, cost, salvage_value, useful_life, "وحدات الإنتاج")
        print(f"  الاستهلاك لكل وحدة: {dep_per_unit:.4f} ريال/وحدة")
        print("\n  أدخل الإنتاج الفعلي لكل سنة:")
        print("-"*62)
        acc = 0
        bv  = cost
        for yr in range(1, useful_life + 1):
            try:
                units = float(input(f"  السنة {yr} - الوحدات المُنتجة: "))
            except ValueError:
                units = 0
            dep  = min(units * dep_per_unit, bv - salvage_value)
            acc += dep
            bv  -= dep
            print(f"  → استهلاك: {dep:,.2f} | مجمع: {acc:,.2f} | قيمة دفترية: {bv:,.2f}")
        print("="*62)

    # ── 5. مقارنة الطرق ─────────────────────────────────────────
    def compare_methods(self):
        print("\n--- 📊 مقارنة طرق الاستهلاك ---\n")
        r = self._get_asset_inputs()
        if not r:
            return
        asset_name, cost, salvage_value, useful_life, dep_cost = r

        sl_annual = dep_cost / useful_life
        ddb_rate  = 2 / useful_life
        syd_sum   = useful_life * (useful_life + 1) / 2

        print("\n" + "="*72)
        print(f"  مقارنة طرق الاستهلاك - {asset_name}")
        print(f"  التكلفة: {cost:,.0f} | القيمة التخريدية: {salvage_value:,.0f} | العمر: {useful_life}سنة")
        print("="*72)
        print(f"  {'السنة':^5} {'القسط الثابت':>14} {'المتناقص×2':>14} {'SYD':>12}")
        print("-"*72)

        ddb_bv = cost
        for yr in range(1, useful_life + 1):
            # SL
            sl = sl_annual
            # DDB
            ddb = ddb_bv * ddb_rate
            if ddb_bv - ddb < salvage_value:
                ddb = max(ddb_bv - salvage_value, 0)
            ddb_bv -= ddb
            # SYD
            remaining = useful_life - yr + 1
            syd = (remaining / syd_sum) * dep_cost
            print(f"  {yr:^5} {sl:>14,.2f} {ddb:>14,.2f} {syd:>12,.2f}")

        print("="*72)
        print("  💡 القسط المتناقص = استهلاك أعلى في السنوات الأولى (مناسب للتقنية)")
        print("  💡 القسط الثابت   = أبسط وأكثر شيوعاً في المطاعم والفنادق")

    # ── 6. إدارة سجل الأصول ─────────────────────────────────────
    def manage_assets(self):
        self._ensure_assets_table()
        while True:
            print("\n--- 🗂️ سجل الأصول الثابتة ---")
            print("1. إضافة أصل جديد")
            print("2. عرض جميع الأصول")
            print("3. الرجوع")
            c = input("اختر: ").strip()
            if c == "1":
                self._add_asset()
            elif c == "2":
                self._list_assets()
            elif c == "3":
                break

    def _ensure_assets_table(self):
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fixed_assets (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name     TEXT    NOT NULL,
                purchase_date  TEXT    NOT NULL,
                cost           REAL    NOT NULL,
                salvage_value  REAL    DEFAULT 0,
                useful_life    INTEGER NOT NULL,
                method         TEXT    DEFAULT 'القسط الثابت',
                category       TEXT    DEFAULT 'معدات',
                notes          TEXT    DEFAULT '',
                created_at     TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()
        conn.close()

    def _add_asset(self):
        print("\n  إضافة أصل ثابت جديد:")
        r = self._get_asset_inputs()
        if not r:
            return
        asset_name, cost, salvage_value, useful_life, _ = r

        purchase_date = input("  تاريخ الشراء (YYYY-MM-DD) [افتراضي اليوم]: ").strip()
        if not purchase_date:
            purchase_date = datetime.now().strftime("%Y-%m-%d")

        methods = ["القسط الثابت", "القسط المتناقص", "مجموع أرقام السنوات"]
        for i, m in enumerate(methods, 1):
            print(f"  {i}. {m}")
        mc = input("  طريقة الاستهلاك (1-3): ").strip()
        method   = methods[int(mc)-1] if mc in ("1","2","3") else "القسط الثابت"
        category = input("  التصنيف (معدات/أثاث/مركبات/مباني): ").strip() or "معدات"

        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fixed_assets (asset_name, purchase_date, cost, salvage_value, useful_life, method, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_name, purchase_date, cost, salvage_value, useful_life, method, category))
        conn.commit()
        conn.close()
        print(f"  ✅ تم إضافة الأصل: {asset_name} | {cost:,.2f} ريال | {useful_life} سنوات")

    def _list_assets(self):
        self._ensure_assets_table()
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fixed_assets ORDER BY purchase_date")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n  📭 لا توجد أصول مسجلة.")
            return

        today      = datetime.now()
        total_cost = 0
        total_book = 0
        print("\n" + "="*75)
        print(f"  {'#':<4} {'الأصل':<22} {'التكلفة':>10} {'تاريخ الشراء':<14} {'العمر':>6} {'القيمة الحالية':>13}")
        print("-"*75)
        for row in rows:
            try:
                purchase      = datetime.strptime(row['purchase_date'], "%Y-%m-%d")
                years_elapsed = (today - purchase).days / 365.25
            except Exception:
                years_elapsed = 0
            dep_yr     = (row['cost'] - row['salvage_value']) / row['useful_life']
            total_dep  = min(dep_yr * years_elapsed, row['cost'] - row['salvage_value'])
            book_value = row['cost'] - total_dep
            total_cost += row['cost']
            total_book += book_value
            print(f"  {row['id']:<4} {row['asset_name']:<22} {row['cost']:>10,.2f} {row['purchase_date']:<14} {row['useful_life']:>4}سنة {book_value:>12,.2f}")
        print("="*75)
        print(f"  الإجمالي:{' '*32}{total_cost:>10,.2f}{'':>22}{total_book:>12,.2f}")
        print(f"  مجمع الاستهلاك: {total_cost-total_book:>10,.2f} ريال")

    # ── 7. تقرير الاستهلاك السنوي ────────────────────────────────
    def annual_depreciation_report(self):
        self._ensure_assets_table()
        try:
            year = int(input(f"  السنة (افتراضي {datetime.now().year}): ").strip() or datetime.now().year)
        except ValueError:
            year = datetime.now().year

        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fixed_assets ORDER BY category, asset_name")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n  📭 لا توجد أصول مسجلة.")
            return

        print("\n" + "="*65)
        print(f"  📋 تقرير الاستهلاك السنوي - {year}")
        print("="*65)
        print(f"  {'الأصل':<22} {'التصنيف':<12} {'الطريقة':<16} {'الاستهلاك':>10}")
        print("-"*65)
        total = 0
        for row in rows:
            dep   = (row['cost'] - row['salvage_value']) / row['useful_life']
            total += dep
            print(f"  {row['asset_name']:<22} {row['category']:<12} {row['method']:<16} {dep:>10,.2f}")
        print("="*65)
        print(f"  إجمالي الاستهلاك السنوي:  {total:>35,.2f} ريال")
        print(f"  الاستهلاك الشهري:          {total/12:>35,.2f} ريال")
        print("="*65)
