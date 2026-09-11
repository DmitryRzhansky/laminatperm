from app.extensions import db
from app.models.settings import utcnow


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    location = db.Column(db.String(255), default="")
    lead = db.Column(db.Text, default="")
    tags = db.Column(db.String(500), default="")
    fact_material = db.Column(db.String(255), default="")
    fact_task = db.Column(db.String(255), default="")
    fact_result = db.Column(db.String(255), default="")
    works = db.Column(db.Text, default="")
    seo_title = db.Column(db.String(255), default="")
    seo_description = db.Column(db.String(500), default="")
    show_on_home = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)

    images = db.relationship(
        "CaseImage",
        backref="case",
        cascade="all, delete-orphan",
        order_by="CaseImage.sort_order",
    )

    @property
    def tag_list(self) -> list[str]:
        return [item.strip() for item in (self.tags or "").split(",") if item.strip()]

    @property
    def work_list(self) -> list[str]:
        return [item.strip() for item in (self.works or "").split("\n") if item.strip()]

    @property
    def cover(self) -> str:
        if self.images:
            return self.images[0].filename
        return ""


class CaseImage(db.Model):
    __tablename__ = "case_images"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False, index=True)
    filename = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
