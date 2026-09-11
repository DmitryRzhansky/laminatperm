from __future__ import annotations

from decimal import Decimal

from flask import session

from app.models import Product


class CartService:
    SESSION_KEY = "cart"

    def _items(self) -> dict:
        return session.setdefault(self.SESSION_KEY, {})

    def add(self, product: Product, quantity: Decimal) -> None:
        items = self._items()
        key = str(product.id)
        current = Decimal(str(items.get(key, "0")))
        items[key] = str(current + quantity)
        session.modified = True

    def update(self, product_id: int, quantity: Decimal) -> None:
        items = self._items()
        key = str(product_id)
        if quantity <= 0:
            items.pop(key, None)
        else:
            items[key] = str(quantity)
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
        products = Product.query.filter(Product.id.in_(ids)).all()
        by_id = {item.id: item for item in products}
        for key, raw_qty in items.items():
            product = by_id.get(int(key))
            if not product:
                continue
            quantity = Decimal(str(raw_qty))
            result.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "sum": quantity * (product.price or 0),
                }
            )
        return result

    def total(self) -> Decimal:
        return sum((item["sum"] for item in self.detailed()), Decimal("0"))

    def count(self) -> int:
        return len(self._items())
