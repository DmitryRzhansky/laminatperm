from app.extensions import db
from app.models.settings import utcnow

FACT_ICONS = (
    "icons/cases/stack.svg",
    "icons/cases/clipboard-text.svg",
    "icons/cases/scales.svg",
)


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    heading = db.Column(db.String(255), default="")
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    location = db.Column(db.String(255), default="")
    lead = db.Column(db.Text, default="")
    tags = db.Column(db.String(500), default="")
    fact_material = db.Column(db.String(255), default="")
    fact_task = db.Column(db.String(255), default="")
    fact_result = db.Column(db.String(255), default="")
    fact_material_label = db.Column(db.String(100), default="Материал")
    fact_task_label = db.Column(db.String(100), default="Задача")
    fact_result_label = db.Column(db.String(100), default="Способ")
    fact_material_icon = db.Column(db.String(255), default=FACT_ICONS[0])
    fact_task_icon = db.Column(db.String(255), default=FACT_ICONS[1])
    fact_result_icon = db.Column(db.String(255), default=FACT_ICONS[2])
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
    def page_heading(self) -> str:
        return (self.heading or self.title or "").strip()

    @property
    def fact_list(self) -> list[dict[str, str]]:
        rows = (
            ("Материал", self.fact_material, FACT_ICONS[0]),
            ("Задача", self.fact_task, FACT_ICONS[1]),
            ("Способ", self.fact_result, FACT_ICONS[2]),
        )
        return [
            {"label": label, "value": (value or "").strip(), "icon": icon}
            for label, value, icon in rows
            if (value or "").strip()
        ]

    @property
    def cover(self) -> str:
        if self.images:
            return self.images[0].filename
        return ""

    @property
    def cover_alt(self) -> str:
        if self.images:
            return self.images[0].alt or self.page_heading
        return self.page_heading


class CaseImage(db.Model):
    __tablename__ = "case_images"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False, index=True)
    filename = db.Column(db.String(500), nullable=False)
    alt = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)
