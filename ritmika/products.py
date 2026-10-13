"""Каталог Ritmika: единый источник данных о товарах и категориях."""

from __future__ import annotations

from dataclasses import dataclass

APPAREL_SIZES: tuple[str, ...] = ("XS", "S", "M", "L", "XL")
ONE_SIZE: tuple[str, ...] = ("One size",)


@dataclass(frozen=True)
class Category:
    """Категория каталога."""

    id: str
    title: str


@dataclass(frozen=True)
class Product:
    """Товар коллекции."""

    id: str
    name: str
    cat: str
    meta: str
    sizes: tuple[str, ...]
    price: int
    img: str
    alt: str
    desc: str


CATEGORIES: tuple[Category, ...] = (
    Category("all", "Все"),
    Category("outer", "Верхняя одежда"),
    Category("knit", "Трикотаж"),
    Category("pants", "Брюки"),
    Category("shirt", "Рубашки и блузы"),
    Category("dress", "Платья и юбки"),
    Category("acc", "Аксессуары"),
)

CATEGORY_TITLES: dict[str, str] = {c.id: c.title for c in CATEGORIES}

PRODUCTS: tuple[Product, ...] = (
    Product(
        "oktava", "Пальто «Октава»", "outer", "Двойная шерсть, песочный",
        APPAREL_SIZES, 24900, "product-coat.jpg",
        "Двубортное пальто песочного оттенка на модели",
        "Пальто прямого силуэта из плотной двусторонней шерсти. Мягкая линия плеча, "
        "глубокие карманы, потайная застёжка. Носится и с кашне, и как самостоятельный акцент.",
    ),
    Product(
        "sinkopa", "Свитер «Синкопа»", "knit", "Крупная вязка, овсяный",
        APPAREL_SIZES, 12400, "product-knit.jpg",
        "Объёмный свитер овсяного оттенка с высоким воротом",
        "Объёмный свитер крупной вязки из шерстяной смеси с высоким воротом. Вязка плотная, "
        "держит форму после стирки.",
    ),
    Product(
        "metronom", "Брюки «Метроном»", "pants", "Шерсть, широкие, графит",
        APPAREL_SIZES, 9800, "product-trousers.jpg",
        "Широкие шерстяные брюки графитового цвета",
        "Широкие брюки со стрелкой и посадкой на талии. Графитовый оттенок сочетается "
        "со всей палитрой коллекции.",
    ),
    Product(
        "nocturn", "Рубашка «Ноктюрн»", "shirt", "Хлопковый поплин, айвори",
        APPAREL_SIZES, 7200, "product-shirt.jpg",
        "Свободная рубашка из хлопкового поплина цвета слоновой кости",
        "Свободная рубашка из плотного хлопкового поплина. Мягкий ворот, удлинённая спинка.",
    ),
    Product(
        "aria", "Платье «Ария»", "dress", "Вискоза, перламутрово-серое",
        APPAREL_SIZES, 14300, "product-dress.jpg",
        "Минималистичное платье перламутрово-серого цвета на тонких бретелях",
        "Платье на тонких бретелях из матовой вискозы с перламутровым отливом.",
    ),
    Product(
        "legato", "Снуд «Легато»", "acc", "Ребристая вязка, меланж",
        ONE_SIZE, 5900, "product-scarf.jpg",
        "Крупный ребристый снуд серой меланжевой вязки",
        "Объёмный снуд ребристой вязки из меланжевой шерсти. Носится в два оборота.",
    ),
    Product(
        "pauza", "Жакет «Пауза»", "outer", "Шерстяной твид, бежевый",
        APPAREL_SIZES, 16900, "product-jacket.jpg",
        "Укороченный жакет из бежевого шерстяного твида",
        "Жакет свободного кроя из мягкого шерстяного твида. Структурное плечо, "
        "накладные карманы, подкладка из вискозы.",
    ),
    Product(
        "takt", "Юбка «Такт»", "dress", "Шерсть, миди, серый меланж",
        APPAREL_SIZES, 8400, "product-skirt.jpg",
        "Шерстяная юбка миди серого меланжа со встречными складками",
        "Юбка миди со встречными складками из шерсти в рубчик. Посадка на талии.",
    ),
    Product(
        "adagio", "Кардиган «Адажио»", "knit", "Крупная вязка, овсяный",
        APPAREL_SIZES, 13200, "product-cardigan.jpg",
        "Кардиган крупной вязки овсяного оттенка с накладными карманами",
        "Кардиган оверсайз крупной вязки с накладными карманами. Тёплый заменитель жакета.",
    ),
    Product(
        "temp", "Брюки «Темп»", "pants", "Хлопковый твил, хаки",
        APPAREL_SIZES, 8900, "product-chinos.jpg",
        "Прямые хлопковые чинос приглушённого хаки",
        "Прямые брюки чинос из плотного хлопкового твила. Посадка средняя.",
    ),
    Product(
        "koda", "Блуза «Кода»", "shirt", "Вискоза, жемчужно-серая",
        APPAREL_SIZES, 7800, "product-blouse.jpg",
        "Струящаяся жемчужно-серая блуза из вискозы",
        "Блуза из струящейся вискозы со сборкой на плечах. Мягко драпируется.",
    ),
    Product(
        "unison", "Водолазка «Унисон»", "knit", "Меринос, графит",
        APPAREL_SIZES, 6700, "product-turtleneck.jpg",
        "Облегающая водолазка из тонкого мериноса графитового цвета",
        "Облегающая водолазка из тонкого мериносового трикотажа. Не колется, не растягивается.",
    ),
)

_BY_ID: dict[str, Product] = {p.id: p for p in PRODUCTS}


def get_product(product_id: str) -> Product | None:
    """Товар по идентификатору или None."""
    return _BY_ID.get(product_id)


def products_by_cat(cat_id: str) -> list[Product]:
    """Товары категории; 'all' возвращает весь каталог."""
    if cat_id == "all":
        return list(PRODUCTS)
    return [p for p in PRODUCTS if p.cat == cat_id]


def similar_to(product: Product, limit: int = 4) -> list[Product]:
    """Товары той же категории, кроме самого товара."""
    same = [p for p in PRODUCTS if p.cat == product.cat and p.id != product.id]
    return same[:limit]


def size_is_valid(product: Product, size: str) -> bool:
    """Проверка, что размер принадлежит товару."""
    return size in product.sizes
