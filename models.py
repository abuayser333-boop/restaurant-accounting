"""
models.py - نماذج البيانات
نظام محاسبة المطاعم
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class InvoiceItem:
    """عنصر في الفاتورة"""
    name: str
    quantity: float
    unit_price: float
    
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total": self.total
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InvoiceItem":
        return cls(
            name=data["name"],
            quantity=data["quantity"],
            unit_price=data["unit_price"]
        )


@dataclass
class Invoice:
    """نموذج الفاتورة"""
    invoice_number: str
    date: str
    items: List[InvoiceItem]
    customer_name: str = "عميل نقدي"
    tax_rate: float = 0.15
    payment_method: str = "نقد"
    status: str = "مدفوعة"
    notes: str = ""
    id: Optional[int] = None
    
    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)
    
    @property
    def tax_amount(self) -> float:
        return self.subtotal * self.tax_rate
    
    @property
    def total_amount(self) -> float:
        return self.subtotal + self.tax_amount
    
    def items_to_json(self) -> str:
        return json.dumps([item.to_dict() for item in self.items], ensure_ascii=False)
    
    @classmethod
    def items_from_json(cls, json_str: str) -> List[InvoiceItem]:
        data = json.loads(json_str)
        return [InvoiceItem.from_dict(d) for d in data]
    
    def display(self):
        """طباعة تفاصيل الفاتورة"""
        print("\n" + "="*50)
        print(f"  فاتورة رقم: {self.invoice_number}")
        print(f"  التاريخ: {self.date}")
        print(f"  العميل: {self.customer_name}")
        print("-"*50)
        print(f"  {'الصنف':<20} {'الكمية':>8} {'السعر':>10} {'الإجمالي':>10}")
        print("-"*50)
        for item in self.items:
            print(f"  {item.name:<20} {item.quantity:>8.2f} {item.unit_price:>10.2f} {item.total:>10.2f}")
        print("-"*50)
        print(f"  {'المجموع الفرعي':<30} {self.subtotal:>10.2f}")
        print(f"  {'ضريبة القيمة المضافة (15%)':<30} {self.tax_amount:>10.2f}")
        print(f"  {'الإجمالي الكلي':<30} {self.total_amount:>10.2f}")
        print(f"  طريقة الدفع: {self.payment_method} | الحالة: {self.status}")
        print("="*50)


@dataclass
class Expense:
    """نموذج المصروف"""
    date: str
    category: str
    description: str
    amount: float
    payment_method: str = "نقد"
    notes: str = ""
    id: Optional[int] = None
    
    # فئات المصروفات المتاحة
    CATEGORIES = [
        "مواد خام",
        "رواتب وأجور",
        "إيجار",
        "كهرباء وماء",
        "صيانة",
        "تسويق وإعلان",
        "معدات ومستلزمات",
        "نقل وشحن",
        "رسوم وضرائب",
        "متفرقات"
    ]
    
    def display(self):
        """طباعة تفاصيل المصروف"""
        print(f"  [{self.id}] {self.date} | {self.category} | {self.description} | {self.amount:.2f} ريال")


@dataclass
class InventoryItem:
    """نموذج عنصر المخزون"""
    item_name: str
    quantity: float
    unit: str
    min_quantity: float
    cost_per_unit: float
    category: str = "عام"
    supplier: str = ""
    id: Optional[int] = None
    
    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.min_quantity
    
    @property
    def total_value(self) -> float:
        return self.quantity * self.cost_per_unit
    
    def display(self):
        """طباعة تفاصيل المادة"""
        status = "⚠️ منخفض" if self.is_low_stock else "✅ كافٍ"
        print(f"  [{self.id}] {self.item_name:<20} {self.quantity:>8.2f} {self.unit:<6} | {status}")
