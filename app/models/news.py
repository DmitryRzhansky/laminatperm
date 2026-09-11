from app.extensions import db
from app.models.settings import utcnow


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    summary = db.Column(db.Text, default="")
    body_md = db.Column(db.Text, default="")
    image = db.Column(db.String(500), default="")
    seo_title = db.Column(db.String(255), default="")
    seo_description = db.Column(db.String(500), default="")
    is_published = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    @property
    def alt(self) -> str:
        return self.title
