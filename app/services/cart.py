from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from flask import session
from sqlalchemy.orm import joinedload

from app.models import Product


class CartService:
    SESSION_KEY = "cart"

    @staticmethod
    def _as_int_qty(raw) -> Decimal:
        try:
            value = Decimal(str(raw).replace(",", "."))
        except Exception:
            return Decimal("0")
        return Decimal(int(value.to_integral_value(rounding=ROUND_HALF_UP)))

    def _items(self) -> dict:
        return session.setdefault(self.SESSION_KEY, {})

    def add(self, product: Product, quantity: Decimal) -> None:
        items = self._items()
        key = str(product.id)
        current = self._as_int_qty(items.get(key, "0"))
        qty = self._as_int_qty(quantity)
        items[key] = str(max(Decimal("0"), current + qty))
        session.modified = True

    def update(self, product_id: int, quantity: Decimal) -> None:
        items = self._items()
        key = str(product_id)
        qty = self._as_int_qty(quantity)
        if qty <= 0:
            items.pop(key, None)
        else:
            items[key] = str(qty)
        session.modified = True

    def clear(self) -> None:
        session[self.SESSION_KEY] = {}
        session.modified = True

    def detailed(self) -> list[dict]:
        items = self._items()
        result = []
        ids = [int(key) for key in items]
        if not ids:
            return result
        products = (
            Product.query.options(
                joinedload(Product.category),
                joinedload(Product.images),
            )
            .filter(Product.id.in_(ids))
            .all()
        )
        by_id = {item.id: item for item in products}
        dirty = False
        for key, raw_qty in list(items.items()):
            product = by_id.get(int(key))
            if not product:
                continue
            quantity = self._as_int_qty(raw_qty)
            if str(quantity) != str(raw_qty):
                if quantity <= 0:
                    items.pop(key, None)
                else:
                    items[key] = str(quantity)
                dirty = True
            if quantity <= 0:
                continue
            result.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "sum": quantity * (product.price or 0),
                }
            )
        if dirty:
            session.modified = True
        return result

    def total(self) -> Decimal:
        return sum((item["sum"] for item in self.detailed()), Decimal("0"))

    def count(self) -> int:
        return len(self._items())
