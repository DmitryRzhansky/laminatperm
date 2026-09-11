from sqlalchemy.orm import joinedload

from app.models import Product


def products_same_brand(product: Product, *, limit: int = 12) -> list[Product]:
    """Published products with the same brand, excluding the current one."""
    brand = (product.brand or "").strip()
    if not brand:
        return []

    return (
        Product.query.options(
            joinedload(Product.category),
            joinedload(Product.images),
        )
        .filter(
            Product.is_published.is_(True),
            Product.brand == brand,
            Product.id != product.id,
        )
        .order_by(Product.sort_order, Product.id)
        .limit(limit)
        .all()
    )
