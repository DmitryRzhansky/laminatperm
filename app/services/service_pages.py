"""Static content for public service pages (/uslugi/)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServicePage:
    slug: str
    title: str
    seo_title: str
    seo_description: str
    intro: str
    price: str
    icon: str
    image: str
    hero_image: str
    hero_cta_primary: str = "Рассчитать стоимость"
    hero_cta_secondary: str = "Другие услуги"
    points: tuple[str, ...] = field(default_factory=tuple)


SERVICE_PAGES: tuple[ServicePage, ...] = (
    ServicePage(
        slug="ukladka-laminata",
        title="Укладка ламината",
        seo_title="Укладка ламината в Перми",
        seo_description=(
            "Профессиональная укладка ламината в Перми: замер, подложка, раскладка, "
            "подрезка и оформление примыканий. Материал и монтаж в одном заказе."
        ),
        intro=(
            "Замковая укладка ламината с подложкой, подрезкой и аккуратным "
            "оформлением примыканий. Подбираем покрытие, считаем метраж и монтируем "
            "с учётом основания и геометрии помещения."
        ),
        price="от 400 ₽/м²",
        icon="icons/services/replan.svg",
        image="images/services/laminate.webp",
        hero_image="images/services/hero/ukladka-laminata.webp",
        points=(
            "Подбор ламината под помещение и бюджет",
            "Расчёт метража, подложки и комплектующих",
            "Укладка с контролем стыков и зазоров",
        ),
    ),
    ServicePage(
        slug="ukladka-spc",
        title="Укладка SPC",
        seo_title="Укладка SPC в Перми",
        seo_description=(
            "Укладка SPC-покрытий в Перми: жёсткий винил с замком для жилых "
            "и коммерческих помещений. Подбор, доставка и монтаж под ключ."
        ),
        intro=(
            "Монтаж жёсткого винила SPC с замковым соединением. Подходит для "
            "влажных зон и помещений с высокой проходимостью — считаем раскладку "
            "и укладываем на подготовленное основание."
        ),
        price="от 300 ₽/м²",
        icon="icons/services/szz.svg",
        image="images/services/spc.webp",
        hero_image="images/services/hero/ukladka-spc.webp",
        points=(
            "Подбор SPC под нагрузку и влажность",
            "Проверка основания перед монтажом",
            "Замковая укладка без лишних порогов",
        ),
    ),
    ServicePage(
        slug="ukladka-kvartsvinila-i-lvt",
        title="Укладка кварцвинила и LVT",
        seo_title="Укладка кварцвинила и LVT в Перми",
        seo_description=(
            "Укладка кварцвинила и LVT в Перми: замковые и клеевые покрытия. "
            "Поможем выбрать формат монтажа и выполним укладку на объекте."
        ),
        intro=(
            "Работаем с замковым и клеевым кварцвинилом / LVT. Выбираем способ "
            "монтажа под основание и назначение помещения, готовим пол и укладываем "
            "покрытие без спешки «на глаз»."
        ),
        price="от 400 ₽/м²",
        icon="icons/services/ndv.svg",
        image="images/services/lvt.webp",
        hero_image="images/services/hero/ukladka-kvartsvinila-i-lvt.webp",
        points=(
            "Замковый и клеевой монтаж LVT",
            "Подбор коллекции и формата плитки",
            "Аккуратная подрезка и примыкания",
        ),
    ),
    ServicePage(
        slug="ukladka-linoleuma",
        title="Укладка линолеума",
        seo_title="Укладка линолеума в Перми",
        seo_description=(
            "Укладка линолеума в Перми: раскрой, стыковка и монтаж рулонных "
            "покрытий. Замер, подбор и укладка с учётом геометрии помещений."
        ),
        intro=(
            "Раскрой и укладка рулонного линолеума с подгонкой по стенам "
            "и проёмам. Считаем раскладку так, чтобы стыков было меньше, "
            "а покрытие легло ровно."
        ),
        price="от 300 ₽/м²",
        icon="icons/services/pdv.svg",
        image="images/services/linoleum.webp",
        hero_image="images/services/hero/ukladka-linoleuma.webp",
        points=(
            "Раскрой под комнату и сложные узлы",
            "Стыковка и холодная сварка при необходимости",
            "Монтаж на подготовленное основание",
        ),
    ),
    ServicePage(
        slug="ukladka-kovrolina",
        title="Укладка ковролина",
        seo_title="Укладка ковролина в Перми",
        seo_description=(
            "Укладка ковролина в Перми для квартир и офисов. Подбор покрытия, "
            "раскрой, фиксация и аккуратное оформление краёв."
        ),
        intro=(
            "Укладка ковролина в жилых и коммерческих помещениях: раскрой, "
            "стыковка и фиксация. Подбираем покрытие под проходимость "
            "и помогаем закрыть пол аккуратно по периметру."
        ),
        price="от 300 ₽/м²",
        icon="icons/services/zso.svg",
        image="images/services/carpet.webp",
        hero_image="images/services/hero/ukladka-kovrolina.webp",
        points=(
            "Подбор ковролина под нагрузку",
            "Раскрой и стыковка без заметных швов",
            "Фиксация и оформление краёв",
        ),
    ),
    ServicePage(
        slug="demontazh-starogo-pokrytiya",
        title="Демонтаж старого покрытия",
        seo_title="Демонтаж старого напольного покрытия в Перми",
        seo_description=(
            "Демонтаж старого ламината, линолеума и других покрытий в Перми "
            "с выносом и утилизацией. Готовим объект к новому полу."
        ),
        intro=(
            "Снимаем старое покрытие аккуратно и готовим помещение к следующему "
            "этапу — выравниванию или новой укладке. При необходимости выносим "
            "и утилизируем строительный мусор."
        ),
        price="по расчёту",
        icon="icons/services/nds.svg",
        image="images/services/demolition.webp",
        hero_image="images/services/hero/demontazh-starogo-pokrytiya.webp",
        points=(
            "Демонтаж ламината, линолеума и других покрытий",
            "Очистка основания после снятия",
            "Вынос и утилизация мусора",
        ),
    ),
    ServicePage(
        slug="podgotovka-osnovaniya",
        title="Подготовка основания",
        seo_title="Подготовка основания пола в Перми",
        seo_description=(
            "Подготовка основания под напольное покрытие в Перми: проверка "
            "перепадов, выравнивание, стяжка и подготовка под тёплый пол."
        ),
        intro=(
            "Проверяем перепады, готовим основание под выбранное покрытие: "
            "выравнивание, полусухая стяжка, подготовка под тёплый пол. "
            "Без нормальной базы укладка не держится долго."
        ),
        price="по расчёту",
        icon="icons/services/waste.svg",
        image="images/services/subfloor.webp",
        hero_image="images/services/hero/podgotovka-osnovaniya.webp",
        points=(
            "Замер перепадов и оценка основания",
            "Выравнивание и полусухая стяжка",
            "Подготовка под тёплый пол при необходимости",
        ),
    ),
    ServicePage(
        slug="montazh-plintusa",
        title="Монтаж плинтуса",
        seo_title="Монтаж напольного плинтуса в Перми",
        seo_description=(
            "Монтаж плинтуса в Перми после укладки покрытия: подбор профиля, "
            "установка, оформление углов и примыканий, в том числе дюрополимер."
        ),
        intro=(
            "Подбираем и устанавливаем плинтус после укладки покрытия. "
            "Работаем с дюрополимерными и другими профилями, закрываем "
            "примыкания и аккуратно оформляем углы."
        ),
        price="по расчёту",
        icon="icons/services/res.svg",
        image="images/services/skirting.webp",
        hero_image="images/services/hero/montazh-plintusa.webp",
        points=(
            "Подбор плинтуса под покрытие и стены",
            "Монтаж с оформлением углов",
            "Пороги и примыкания при необходимости",
        ),
    ),
)

SERVICES_BY_SLUG = {item.slug: item for item in SERVICE_PAGES}


def get_service(slug: str) -> ServicePage | None:
    return SERVICES_BY_SLUG.get(slug)


def related_services(slug: str, limit: int = 4) -> list[ServicePage]:
    current = get_service(slug)
    if current is None:
        return list(SERVICE_PAGES[:limit])
    others = [item for item in SERVICE_PAGES if item.slug != slug]
    return others[:limit]
