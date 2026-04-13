"""Pre-scraped menus for Holy Greens Västra Hamnen and Dockside Burgers Västra Hamnen.

These menus are scraped multiple times and hardcoded so they are available instantly
without triggering the AI agent scraper on every admin visit.
"""

from __future__ import annotations

from .models import MenuItem

HOLY_GREENS_ITEMS: list[MenuItem] = [
    # ── Hot Bowls ────────────────────────────────────────────────────────────
    MenuItem(
        name="Avogoodness",
        price=144,
        category="main",
        subcategory="Hot Bowls",
        description="Warm Bjäre chicken or vegan bites with black rice, avocado, broccoli trees, red cabbage, lemon crème, roasted shallots, and Green Goddess dressing.",
    ),
    MenuItem(
        name="Thai-ish",
        price=142,
        category="main",
        subcategory="Hot Bowls",
        description="Warm Bjäre chicken or veggie bites with black rice, Asian coleslaw, broccoli, spinach, bean sprouts, coriander, roasted cashews, and mango-lime dressing.",
    ),
    MenuItem(
        name="Beef Vietnam",
        price=138,
        category="main",
        subcategory="Hot Bowls",
        description="Warm slow-cooked beef or veggie bites on glass noodles with cucumber, pickled ginger carrot, red cabbage, chili, green onions, bean sprouts, coriander, and peanut-lime dressing.",
    ),
    MenuItem(
        name="Holy Guacamole",
        price=144,
        category="main",
        subcategory="Hot Bowls",
        description="Warm marinated chicken or vegan bites with black rice, fresh guacamole, broccoli trees, and a paprika-chili dressing.",
    ),
    MenuItem(
        name="Holylulu",
        price=134,
        category="main",
        subcategory="Hot Bowls",
        description="Raw marinated salmon served on a bed of black rice and salad mix with a coriander-lime dressing.",
    ),
    # ── Sallader ─────────────────────────────────────────────────────────────
    MenuItem(
        name="Grönsakslandet Vegansk",
        price=114,
        category="main",
        subcategory="Sallader",
        description="Fresh vegan salad mix with white quinoa, pickled ginger carrots, broccoli trees, cucumber, avocado, beetroot hummus, bean sprouts, sunflower seeds, and basil-lemon dressing.",
    ),
    MenuItem(
        name="Italian Classic (by Smeg)",
        price=154,
        category="main",
        subcategory="Sallader",
        description="Marinated chicken on a classic salad with quinoa and fresh vegetables, drizzled with blood orange vinaigrette.",
    ),
    MenuItem(
        name="Asiatisk Räka",
        price=136,
        category="main",
        subcategory="Sallader",
        description="Hand-peeled shrimp on a salad mix with glass noodles, pickled ginger carrots, edamame beans, paprika, roasted peanuts, coriander, and habanero-lime dressing.",
    ),
    MenuItem(
        name="Laxokado",
        price=142,
        category="main",
        subcategory="Sallader",
        description="Oven-baked salmon on black rice topped with avocado and a healthy mix of fresh vegetables.",
    ),
    MenuItem(
        name="Holy Caesar",
        price=134,
        category="main",
        subcategory="Sallader",
        description="Marinated chicken on a classic Caesar salad with Grana Padano cheese and rich Caesar dressing.",
    ),
    MenuItem(
        name="Mexicali",
        price=134,
        category="main",
        subcategory="Sallader",
        description="Warm slow-cooked beef or veggie bites with salad mix, black rice, chipotle crème, broccoli trees, pickled red onion, mango, avocado, corn chips, and paprika-chili dressing.",
    ),
    # ── Frukost ──────────────────────────────────────────────────────────────
    MenuItem(
        name="Egg & Kale Bowl",
        price=94,
        category="main",
        subcategory="Frukost",
        description="Nutritious black rice with marinated kale, egg, lemon crème, baby tomatoes, parsley, and pumpkin seeds.",
    ),
    MenuItem(
        name="Eggokado Bowl",
        price=94,
        category="main",
        subcategory="Frukost",
        description="Black rice topped with egg, avocado, spinach, sunflower seeds, and Green Goddess dressing.",
    ),
    # ── Dessert ──────────────────────────────────────────────────────────────
    MenuItem(
        name="Chiapudding",
        price=57,
        category="dessert",
        description="Chia pudding with coconut milk and lemon zest, topped with blueberries and granola.",
    ),
    MenuItem(
        name="Kvarg: Vanilj",
        price=57,
        category="dessert",
        description="Creamy vanilla quark topped with marinated mango and coco crunch.",
    ),
    MenuItem(
        name="Overnight Oats",
        price=57,
        category="dessert",
        description="Overnight oats with chia seeds, apple, oat milk, and cinnamon, topped with raspberry compote and granola.",
    ),
    # ── Dryck ────────────────────────────────────────────────────────────────
    MenuItem(
        name="Råsaft: Ananas-Spenat",
        price=42,
        category="drink",
        description="Cold-pressed juice with apple, pineapple, and spinach.",
    ),
    MenuItem(
        name="Råsaft: Morot-Ingefära",
        price=42,
        category="drink",
        description="Cold-pressed juice with apple, orange, carrot, and ginger.",
    ),
    MenuItem(
        name="Råsaft: Apelsin",
        price=42,
        category="drink",
        description="Pure cold-pressed orange juice.",
    ),
    MenuItem(
        name="Råsaft: Rödbeta-Citron-Ingefära",
        price=42,
        category="drink",
        description="Cold-pressed juice with apple, orange, beet, lemon, and ginger.",
    ),
]

DOCKSIDE_ITEMS: list[MenuItem] = [
    # ── Burgers ──────────────────────────────────────────────────────────────
    MenuItem(
        name="Cheese Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Swedish organic grass-fed beef with cheddar cheese, caramelized onions, silver onions, mustard, ketchup, and mayo.",
    ),
    MenuItem(
        name="BBQ Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Swedish organic grass-fed beef with cheddar cheese, crispy bacon, pickled red onion, house BBQ sauce, and mayo.",
    ),
    MenuItem(
        name="Jalapeño Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Swedish organic grass-fed beef with cheddar cheese, jalapeño spread, caramelized onions, and house BBQ sauce.",
    ),
    MenuItem(
        name="American Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Swedish organic grass-fed beef with cheddar cheese, bacon, pickled cucumber, tomato, lettuce, red onion, house dressing, and mayo.",
    ),
    MenuItem(
        name="Halloumi Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Grilled halloumi cheese with pickled red onion, tomato, lettuce, BBQ sauce, and mayo.",
    ),
    MenuItem(
        name="Vegan Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Plant-based bean burger with caramelized onions, BBQ sauce, and vegan mayo.",
    ),
    MenuItem(
        name="Månadens Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Our special burger of the month crafted with unique seasonal flavors — ask staff for today's creation.",
    ),
    MenuItem(
        name="Glutenfri Burger",
        price=125,
        category="main",
        subcategory="BURGERS",
        description="Any burger of your choice served in a gluten-free bun or as a salad wrap.",
    ),
    # ── Tillbehör ─────────────────────────────────────────────────────────────
    MenuItem(
        name="Chilicheese",
        price=45,
        category="side",
        description="Four crispy chili cheese bites.",
    ),
    MenuItem(
        name="Mozzarellasticks",
        price=45,
        category="side",
        description="Four golden mozzarella sticks, perfect for dipping.",
    ),
    MenuItem(
        name="Lökringar",
        price=45,
        category="side",
        description="Five golden crispy onion rings.",
    ),
    # ── Dipsåsar ──────────────────────────────────────────────────────────────
    MenuItem(
        name="Dipsås: Chilimajo",
        price=12,
        category="side",
        description="Spicy chili mayo dip.",
    ),
    MenuItem(
        name="Dipsås: Tryffelmajo",
        price=12,
        category="side",
        description="Rich and decadent truffle mayo dip.",
    ),
    MenuItem(
        name="Dipsås: Vitlöksaioli",
        price=12,
        category="side",
        description="Creamy garlic aioli dip.",
    ),
    MenuItem(
        name="Dipsås: Smält Cheddar",
        price=12,
        category="side",
        description="Melted cheddar dip.",
    ),
    MenuItem(
        name="Dipsås: Wasabiketchup",
        price=12,
        category="side",
        description="Ketchup with a spicy wasabi kick.",
    ),
    MenuItem(
        name="Dipsås: Majonnäs",
        price=12,
        category="side",
        description="Classic creamy mayonnaise.",
    ),
    MenuItem(
        name="Dipsås: BBQ-sås",
        price=12,
        category="side",
        description="Sweet and tangy house BBQ sauce.",
    ),
    MenuItem(
        name="Dipsås: Vegansk Majonnäs",
        price=12,
        category="side",
        description="Creamy vegan mayonnaise.",
    ),
    # ── Övrigt ────────────────────────────────────────────────────────────────
    MenuItem(
        name="Dubbla din burgare",
        price=49,
        category="other",
        description="Double your burger patty for an extra hearty meal.",
    ),
]

CACHED_RESTAURANTS: list[dict] = [
    {"restaurant_name": "Holy Greens", "items": HOLY_GREENS_ITEMS},
    {"restaurant_name": "Dockside Burgers", "items": DOCKSIDE_ITEMS},
]
