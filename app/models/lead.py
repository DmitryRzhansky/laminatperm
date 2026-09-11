from app.extensions import db
from app.models.settings import utcnow  # noqa: F401


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), default="")
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(255), default="")
    product = db.Column(db.String(255), default="")
    details = db.Column(db.Text, default="")
    status = db.Column(db.String(32), default="new", index=True)
    source = db.Column(db.String(64), default="consultation")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
