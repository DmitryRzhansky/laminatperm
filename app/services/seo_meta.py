"""Canonical, Open Graph helpers and JSON-LD builders for public pages."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

from flask import current_app, request, url_for

from app.utils.settings import get_setting

SITE_NAME = "Ламинейшен"
DEFAULT_LOGO = "images/logo.png"
PRICE_RE = re.compile(r"(\d[\d\s]*)")


def site_base_url() -> str:
    configured = (current_app.config.get("SITE_URL") or "").strip().rstrip("/")
    if configured:
        return configured
    return (request.url_root or "").rstrip("/")


def absolute_url(path: str | None = None) -> str:
    """Build an absolute URL for a path or the current request path (no query)."""
    base = site_base_url()
    if path is None:
        path = request.path or "/"
    text = str(path).strip()
    if text.startswith(("http://", "https://")):
        return text
    if not text.startswith("/"):
        text = "/" + text
    return urljoin(base + "/", text.lstrip("/"))


def absolute_media(path: str | None) -> str:
    if not path:
        return default_og_image()
    text = str(path).strip()
    if text.startswith(("http://", "https://")):
        return text
    if text.startswith("/"):
        return absolute_url(text)
    return absolute_url("/static/" + text.lstrip("/"))


def default_og_image() -> str:
    return absolute_url(url_for("static", filename=DEFAULT_LOGO))


def canonical_url() -> str:
    return absolute_url(request.path or "/")


def organization_ld() -> dict[str, Any]:
    phone = get_setting("header.phone", "+7 (909) 112-52-05")
    email = get_setting("contacts.email", "vip.shapen@mail.ru")
    address = get_setting("header.address", "Агатовая улица, 28, Пермь")
    hours = get_setting("header.hours", "7 дней в неделю: 09:00–20:00")
    base = site_base_url()
    return {
        "@context": "https://schema.org",
        "@type": "HomeGoodsStore",
        "@id": f"{base}/#organization",
        "name": SITE_NAME,
        "url": base + "/",
        "logo": default_og_image(),
        "image": default_og_image(),
        "telephone": phone,
        "email": email,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address,
            "addressLocality": "Пермь",
            "addressRegion": "Пермский край",
            "addressCountry": "RU",
        },
        "openingHours": hours,
        "areaServed": {
            "@type": "City",
            "name": "Пермь",
        },
        "sameAs": [
            "https://vk.com/permi/",
        ],
    }


def website_ld() -> dict[str, Any]:
    base = site_base_url()
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{base}/#website",
        "name": SITE_NAME,
        "url": base + "/",
        "publisher": {"@id": f"{base}/#organization"},
        "inLanguage": "ru-RU",
    }


def webpage_ld(
    *,
    name: str,
    description: str = "",
    path: str | None = None,
    page_type: str = "WebPage",
) -> dict[str, Any]:
    url = absolute_url(path)
    base = site_base_url()
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": name,
        "url": url,
        "isPartOf": {"@id": f"{base}/#website"},
        "about": {"@id": f"{base}/#organization"},
        "inLanguage": "ru-RU",
    }
    if description:
        data["description"] = description
    return data


def breadcrumb_ld(crumbs: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    if not crumbs:
        return None
    elements = []
    position = 1
    for crumb in crumbs:
        label = (crumb.get("label") or "").strip()
        if not label:
            continue
        item: dict[str, Any] = {
            "@type": "ListItem",
            "position": position,
            "name": label,
        }
        url = crumb.get("url")
        if url:
            item["item"] = absolute_url(url)
        elements.append(item)
        position += 1
    if not elements:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


def faq_ld(items: list[Any], *, path: str | None = None) -> dict[str, Any] | None:
    entities = []
    for item in items or []:
        question = (getattr(item, "question", None) or "").strip()
        answer = (getattr(item, "answer", None) or "").strip()
        if not question or not answer:
            continue
        entities.append(
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer,
                },
            }
        )
    if not entities:
        return None
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    if path is not None:
        data["url"] = absolute_url(path)
    return data


def offer_price(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = PRICE_RE.search(text.replace("\xa0", " "))
    if not match:
        return None
    digits = re.sub(r"\s+", "", match.group(1))
    return digits or None


def product_ld(product, *, product_title: str, path: str | None = None) -> dict[str, Any]:
    url = absolute_url(path)
    images = [absolute_media(img.filename) for img in (product.images or []) if img.filename]
    if not images and product.cover:
        images = [absolute_media(product.cover)]
    description = (
        (product.seo_description or "").strip()
        or (product.short_description or "").strip()
        or product_title
    )
    price = offer_price(product.price)
    offer: dict[str, Any] = {
        "@type": "Offer",
        "url": url,
        "priceCurrency": "RUB",
        "availability": "https://schema.org/InStock",
        "itemCondition": "https://schema.org/NewCondition",
        "seller": {
            "@type": "Organization",
            "name": SITE_NAME,
        },
    }
    if price:
        offer["price"] = price
    unit = getattr(product, "unit", "m2")
    if unit == "m2":
        offer["unitText"] = "м²"
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product_title,
        "description": description,
        "url": url,
        "offers": offer,
    }
    if images:
        data["image"] = images if len(images) > 1 else images[0]
    if product.sku:
        data["sku"] = product.sku
        data["mpn"] = product.sku
    if product.brand:
        data["brand"] = {"@type": "Brand", "name": product.brand}
    if product.category is not None:
        data["category"] = product.category.name
    return data


def service_ld(service, *, path: str | None = None) -> dict[str, Any]:
    url = absolute_url(path)
    name = service.display_heading or service.title
    description = (
        (service.seo_description or "").strip()
        or (service.intro or "").strip()
        or (service.text or "").strip()
        or name
    )
    image = service.hero_image or service.image
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name,
        "description": description,
        "url": url,
        "provider": {
            "@type": "HomeGoodsStore",
            "name": SITE_NAME,
            "url": site_base_url() + "/",
        },
        "areaServed": {"@type": "City", "name": "Пермь"},
    }
    if image:
        data["image"] = absolute_media(image)
    price = offer_price(service.price)
    if price or (service.price or "").strip():
        offer: dict[str, Any] = {
            "@type": "Offer",
            "priceCurrency": "RUB",
            "url": url,
            "availability": "https://schema.org/InStock",
        }
        if price:
            offer["price"] = price
        else:
            offer["description"] = (service.price or "").strip()
        data["offers"] = offer
    return data


def news_article_ld(item, *, path: str | None = None) -> dict[str, Any]:
    url = absolute_url(path)
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": item.title,
        "description": (item.seo_description or item.summary or item.title).strip(),
        "url": url,
        "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": default_og_image(),
            },
        },
        "inLanguage": "ru-RU",
    }
    if item.image:
        data["image"] = [absolute_media(item.image)]
    if item.published_at:
        data["datePublished"] = item.published_at.isoformat()
    if item.updated_at:
        data["dateModified"] = item.updated_at.isoformat()
    return data


def case_ld(item, *, path: str | None = None) -> dict[str, Any]:
    url = absolute_url(path)
    heading = item.page_heading
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": heading,
        "description": (item.seo_description or item.lead or heading).strip(),
        "url": url,
        "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": default_og_image(),
            },
        },
        "inLanguage": "ru-RU",
    }
    if item.cover:
        data["image"] = [absolute_media(item.cover)]
    if item.location:
        data["contentLocation"] = {
            "@type": "Place",
            "name": item.location,
        }
    if item.created_at:
        data["datePublished"] = item.created_at.isoformat()
    return data


def item_list_ld(
    *,
    name: str,
    items: list[dict[str, Any]],
    path: str | None = None,
    description: str = "",
) -> dict[str, Any]:
    elements = []
    for index, entry in enumerate(items, start=1):
        element: dict[str, Any] = {
            "@type": "ListItem",
            "position": index,
            "name": entry.get("name") or "",
        }
        if entry.get("url"):
            element["url"] = absolute_url(entry["url"])
        if entry.get("item"):
            element["item"] = entry["item"]
        elements.append(element)
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "itemListElement": elements,
    }
    if path is not None:
        data["url"] = absolute_url(path)
    if description:
        data["description"] = description
    return data


def collect_json_ld(*blocks: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [block for block in blocks if block]
