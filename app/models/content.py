from app.extensions import db
from app.models.settings import utcnow


class SitePage(db.Model):
    """Simple inner pages: promo, warranty, payment, delivery."""

    __tablename__ = "site_pages"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    h1 = db.Column(db.String(255), default="")
    summary = db.Column(db.Text, default="")
    points = db.Column(db.Text, default="")
    body_md = db.Column(db.Text, default="")
    image = db.Column(db.String(500), default="")
    seo_title = db.Column(db.String(255), default="")
    seo_description = db.Column(db.String(500), default="")
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    @property
    def points_list(self) -> list[str]:
        text = (self.points or "").strip()
        if not text:
            return []
        return [line.strip("-• \t") for line in text.splitlines() if line.strip()]



class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), default="")
    text = db.Column(db.Text, default="")
    photo = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


class Advantage(db.Model):
    __tablename__ = "advantages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, default="")
    icon = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    heading = db.Column(db.String(255), default="")
    text = db.Column(db.Text, default="")
    intro = db.Column(db.Text, default="")
    body_md = db.Column(db.Text, default="")
    price = db.Column(db.String(120), default="")
    image = db.Column(db.String(500), default="")
    hero_image = db.Column(db.String(500), default="")
    icon = db.Column(db.String(500), default="")
    seo_title = db.Column(db.String(255), default="")
    seo_description = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)

    faqs = db.relationship(
        "ServiceFaq",
        backref="service",
        cascade="all, delete-orphan",
        order_by="ServiceFaq.sort_order",
    )

    @property
    def body(self) -> list[str]:
        text = (self.body_md or "").strip()
        if not text:
            return []
        return [part.strip() for part in text.split("\n\n") if part.strip()]

    @property
    def display_heading(self) -> str:
        return (self.heading or self.title or "").strip()


class ServiceFaq(db.Model):
    __tablename__ = "service_faqs"

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False, index=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, default="")
    sort_order = db.Column(db.Integer, default=0)



class Partner(db.Model):
    __tablename__ = "partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, default="")
    url = db.Column(db.String(500), default="")
    image = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(32), default="avito", index=True)
    author = db.Column(db.String(255), default="")
    role = db.Column(db.String(120), default="")
    text = db.Column(db.Text, default="")
    item = db.Column(db.String(255), default="")
    date_text = db.Column(db.String(120), default="")
    rating = db.Column(db.Integer, default=5)
    avatar = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)

    photos = db.relationship(
        "ReviewPhoto",
        backref="review",
        cascade="all, delete-orphan",
        order_by="ReviewPhoto.sort_order",
    )


class ReviewPhoto(db.Model):
    __tablename__ = "review_photos"

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id"), nullable=False, index=True)
    filename = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


class FaqItem(db.Model):
    __tablename__ = "faq_items"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, default="")
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)


class ProcessVideo(db.Model):
    __tablename__ = "process_videos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), default="")
    embed_url = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


class GalleryImage(db.Model):
    __tablename__ = "gallery_images"

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(64), default="about", index=True)
    filename = db.Column(db.String(500), nullable=False)
    alt = db.Column(db.String(255), default="")
    sort_order = db.Column(db.Integer, default=0)


class AboutStat(db.Model):
    __tablename__ = "about_stats"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(64), nullable=False)
    label = db.Column(db.String(255), default="")
    sort_order = db.Column(db.Integer, default=0)
