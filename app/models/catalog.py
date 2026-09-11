from app.extensions import db
from app.models.settings import utcnow


class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    intro = db.Column(db.Text, default="")
    cover = db.Column(db.String(500), default="")
    seo_title = db.Column(db.String(255), default="")
    seo_description = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)

    products = db.relationship("Product", backref="category", lazy="dynamic")


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id"), nullable=False, index=True)
    brand = db.Column(db.String(120), default="", index=True)
    price = db.Column(db.Numeric(12, 2), default=0)
    old_price = db.Column(db.Numeric(12, 2), nullable=True)
    unit = db.Column(db.String(16), default="m2")
    sku = db.Column(db.String(120), default="")
    short_description = db.Column(db.Text, default="")
    description_md = db.Column(db.Text, default="")
    description_html = db.Column(db.Text, default="")
    seo_title = db.Column(db.String(255), default="")
    seo_description = db.Column(db.String(500), default="")
    tilda_uid = db.Column(db.String(64), unique=True, nullable=True, index=True)
    is_published = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    images = db.relationship(
        "ProductImage",
        backref="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )
    attributes = db.relationship(
        "ProductAttribute",
        backref="product",
        cascade="all, delete-orphan",
        order_by="ProductAttribute.sort_order",
    )
    faqs = db.relationship(
        "ProductFaq",
        backref="product",
        cascade="all, delete-orphan",
        order_by="ProductFaq.sort_order",
    )

    @property
    def cover(self) -> str:
        if self.images:
            return self.images[0].filename
        return ""

    @property
    def unit_label(self) -> str:
        return "₽/м²" if self.unit == "m2" else "₽/шт"

    def attr(self, name: str) -> str:
        for item in self.attributes:
            if item.name.lower() == name.lower():
                return item.value
        return ""


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    filename = db.Column(db.String(500), nullable=False)
    alt = db.Column(db.String(255), default="")
    sort_order = db.Column(db.Integer, default=0)


class ProductAttribute(db.Model):
    __tablename__ = "product_attributes"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    value = db.Column(db.String(255), default="")
    sort_order = db.Column(db.Integer, default=0)


class ProductFaq(db.Model):
    __tablename__ = "product_faqs"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, default="")
    sort_order = db.Column(db.Integer, default=0)


class ProductRedirect(db.Model):
    __tablename__ = "product_redirects"

    id = db.Column(db.Integer, primary_key=True)
    tilda_uid = db.Column(db.String(64), unique=True, nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(255), default="")
    delivery_method = db.Column(db.String(64), default="pickup")
    address = db.Column(db.Text, default="")
    payment_method = db.Column(db.String(64), default="cash")
    comment = db.Column(db.Text, default="")
    status = db.Column(db.String(32), default="new", index=True)
    total = db.Column(db.Numeric(12, 2), default=0)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    items = db.relationship(
        "OrderItem",
        backref="order",
        cascade="all, delete-orphan",
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(16), default="m2")
    quantity = db.Column(db.Numeric(12, 2), default=1)
    price = db.Column(db.Numeric(12, 2), default=0)
