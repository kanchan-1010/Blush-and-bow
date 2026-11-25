import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "blush_and_bow.db"))

if os.path.dirname(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        cat_label TEXT NOT NULL,
        price INTEGER NOT NULL,
        mrp INTEGER NOT NULL,
        cost INTEGER NOT NULL,
        stock INTEGER NOT NULL DEFAULT 50,
        badge TEXT,
        rating REAL DEFAULT 5.0,
        reviews_count INTEGER DEFAULT 0,
        icon TEXT DEFAULT '🌸',
        description TEXT,
        details TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        shipping_address TEXT NOT NULL,
        city TEXT NOT NULL,
        pincode TEXT NOT NULL,
        subtotal INTEGER NOT NULL,
        discount INTEGER DEFAULT 0,
        shipping_fee INTEGER DEFAULT 0,
        total INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        order_status TEXT DEFAULT 'processing',
        tracking_number TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. Order Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        price INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    ''')

    # 4. Coupons Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_percent INTEGER NOT NULL,
        min_order INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )
    ''')

    # 5. Subscribers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Seed Coupons
    cursor.execute("SELECT COUNT(*) FROM coupons")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO coupons (code, discount_percent, min_order, is_active) VALUES ('PRETTY10', 10, 0, 1)")
        cursor.execute("INSERT INTO coupons (code, discount_percent, min_order, is_active) VALUES ('WELCOME10', 10, 0, 1)")

    # Seed Products
    seed_products = [
        # GIFT COMBOS
        ("BNB-GC-001", "The Signature 'Pretty Moments' Hamper", "gifts", "Gift Combos", 1499, 1999, 480, 25, "Luxury Hamper", 5.0, 96, "🎁",
         "Includes oversized Blush Silk Bow, 18k Gold Crystal Bloom Ring, Handcrafted Honey Teddy Bear Charm, and deckle-edge calligraphy card in a rigid keepsake box.",
         "Rigid magnetic pink keepsake box • 4 signature pieces • Scented crinkle tissue • Satin ribbon tied"),
        ("BNB-GC-002", "The 'Pastel Garden Dream' Gift Hamper", "gifts", "Gift Combos", 1099, 1499, 350, 30, "Bestseller Hamper", 5.0, 64, "💐",
         "Handcrafted Mini Tulip Bouquet Bow Keychain, trio of lustrous pastel silk scrunchies, dainty rose gold heart drop earrings, and a 'Bloom With Joy' calligraphy card.",
         "Blush presentation keepsake box • 4 curated treats • Crinkle paper lining • Ready to gift"),
        ("BNB-GC-003", "The 'Golden Sunshine & Bloom' Gift Box", "gifts", "Gift Combos", 899, 1199, 280, 35, "Warmth & Joy", 4.9, 52, "🌻",
         "Pair of handcrafted Twin Golden Sunflower Keychains, sparkling Blooming Crystal Blossom Ring, and handwritten note in our signature blush gift box.",
         "Signature gift box • Handcrafted sunflower duo & crystal ring • Personalized note card"),
        ("BNB-GC-004", "The 'Good Vibes & Protection' Nazar Box", "gifts", "Gift Combos", 999, 1299, 310, 30, "Nazar Protection", 5.0, 43, "🧿",
         "Handcrafted Royal Blue Evil Eye Flower Keychain Trio, Dainty Rose Gold Heart Earrings, and 'Positive Energy' keepsake affirmation card.",
         "Blush keepsake box • 3 Evil Eye charms & heart earrings • Affirmation gift card"),
        ("BNB-GC-005", "The 'BFF Cuddle & Sparkle' Duo Box", "gifts", "Gift Combos", 749, 999, 230, 40, "Friendship Box", 4.9, 37, "🧸",
         "Handcrafted Cuddly Honey Teddy Bear Keychain, Pearl Center Blossom Flower Keychain, and Rose Velvet Bow Hair Tie.",
         "Cute keepsake gift box • 2 handcrafted keychains & hair bow • Perfect for birthdays & besties"),
        ("BNB-GC-006", "Sunflower & Silk Happiness Gift Box", "gifts", "Gift Combos", 799, 1099, 250, 35, "Gift Favorite", 4.9, 47, "💐",
         "Handcrafted Golden Sunflower Keychain, Silk Satin Bow Clip, and handwritten message note.",
         "Blush presentation box • Set of 2 signature pieces • Ready to gift"),

        # KEYCHAINS
        ("BNB-KC-001", "Handcrafted Royal Blue Evil Eye Flower Trio", "keychains", "Keychains", 249, 349, 75, 60, "Protection Charm", 5.0, 58, "🧿",
         "Handcrafted royal blue plush flower keychains featuring the traditional Nazar / Evil Eye design. Believed to bring positive energy and good fortune.",
         "Material: Plush Chenille • Design: Traditional Nazar Evil Eye • Silver Keyring • Set of 3 Keychains"),
        ("BNB-KC-002", "Cuddly Honey Teddy Bear Plush Keychain Duo", "keychains", "Keychains", 249, 349, 70, 60, "Customer Favorite", 5.0, 82, "🧸",
         "Ultra-cute handcrafted honey-tan teddy bear head keychains featuring fluffy plush ears, sweet embroidered muzzles, and sturdy silver chains.",
         "Material: Fluffy Chenille Plush • Embroidered Face Details • Set of 2 Teddy Charms • Steel Keyring"),
        ("BNB-KC-003", "Handcrafted Mini Tulip Bouquet Bow Keychains", "keychains", "Keychains", 269, 380, 75, 50, "Boutique Special", 5.0, 71, "🌷",
         "Exquisite hand-tied mini tulip bouquet charms: tri-color pastel tulips gracefully wrapped with a hand-tied ribbon bow and faux pearl stud.",
         "Material: Plush chenille tulips • Ribbon bow with pearl bead • Set of 2 Bouquets • Sturdy chain"),
        ("BNB-KC-004", "Pearl Center Blossom Flower Keychain Pair", "keychains", "Keychains", 229, 320, 65, 60, "New Launch", 5.0, 49, "🌸",
         "Handcrafted 5-petal plush flower keychains in Rose Pink and Periwinkle Blue, adorned with a delicate lustrous pearl centerpiece and fresh green leaf backing.",
         "Material: Chenille plush petals • Central pearl bead • Green leaf backing • Pair of 2"),
        ("BNB-KC-005", "Twin Golden Sunflower Sunshine Keychains", "keychains", "Keychains", 249, 349, 70, 50, "Sunshine Duo", 4.9, 67, "🌻",
         "A cheerful duo of handcrafted golden yellow sunflowers with deep velvety brown centers and green leaf accents. Sturdy silver keyrings attached.",
         "Material: Velvet chenille texture • Green leaf accent • Set of 2 Sunflowers • Steel chain"),
        ("BNB-KC-006", "Pastel Blossom Daisy Rainbow Keychains", "keychains", "Keychains", 189, 260, 50, 75, "Pastel Mix", 4.9, 54, "🌸",
         "Handcrafted pastel daisy flower keychains in dreamy soft tones: Sky Blue, Lavender Purple, Blossom Pink, Pure White, and Mint Green with sunny centers.",
         "Material: Plush chenille yarn • Diameter: 6cm • Silver finish keyring • Super soft feel"),
        ("BNB-KC-007", "Garden Bloom Stem Flower Keychains", "keychains", "Keychains", 219, 299, 60, 65, "Trending", 5.0, 38, "🌷",
         "Delicate handcrafted floral stem keychains featuring lush green leaf stems: White Daisy, Golden Sunflower, Sky Blue Tulip, and Rose Pink Tulip charms.",
         "Material: Chenille stem petals & leaves • Length: ~10cm with chain • Steel key ring"),
        ("BNB-KC-008", "Handcrafted Rainbow Cloud Plush Keychain Duo", "keychains", "Keychains", 229, 320, 65, 50, "Cloud Duo", 5.0, 56, "☁️",
         "Two adorable plush rainbow cloud keychains handcrafted in pastel colours with a soft fuzzy finish and tiny star details, perfect for your bag, purse, or backpack.",
         "Material: Plush chenille clouds • Pastel rainbow colours • Silver tone chain • Set of 2"),

        # JEWELLERY
        ("BNB-JW-001", "Blooming Crystal Blossom Floral Ring", "jewellery", "Jewellery", 449, 649, 135, 60, "Bestseller", 5.0, 46, "💍",
         "Exquisite blooming floral cluster ring in a rich 18k gold-tone finish. Embellished with sparkling baguette-cut and brilliant round cubic zirconia crystal petals.",
         "18k Gold Finish • Premium Baguette Cubic Zirconia • Adjustable Free Size • Hypoallergenic & Skin-Safe"),
        ("BNB-JW-002", "Eternity Triple-Row Stacking Band Ring", "jewellery", "Jewellery", 499, 699, 150, 50, "Trending", 4.9, 63, "✨",
         "Glamorous triple-layer gold eternity band micro-paved with radiant crystal stones, featuring dual focal accents: a chic square cushion cluster and a round solitaire.",
         "18k Gold Finish • 3-Row Micro-Pave Band • Dual Cluster Settings • Adjustable Free Size Band"),
        ("BNB-JW-003", "Dainty Rose Gold Heart Drop Earrings", "jewellery", "Jewellery", 649, 899, 175, 50, "Favorite", 4.9, 175, "✨",
         "Delicate open-heart drops plated in 18k rose gold with sparkling micro-cubic zirconia accents.",
         "18k Rose Gold Plating • Hypoallergenic • Anti-tarnish brass"),
        ("BNB-JW-004", "Freshwater Seed Pearl Choker", "jewellery", "Jewellery", 899, 1199, 260, 25, "Luxury", 4.8, 52, "📿",
         "Hand-strung genuine mini seed pearls featuring a delicate gold bow center charm.",
         "38cm + 5cm extender • Natural freshwater seed pearls • Lobster clasp"),

        # HAIR ACCESSORIES
        ("BNB-HA-001", "Luxe Silk Satin Bow Barrette (Blush)", "hair", "Hair Accessories", 449, 599, 130, 45, "Bestseller", 4.9, 142, "🎀",
         "Handcrafted oversized French barrette fashioned from heavy Mulberry satin silk in signature Blush Pink.",
         "100% Silk Satin • 8cm French steel barrette • Crease-free hold"),
        ("BNB-HA-002", "Rose Velvet Oversized Hair Bow", "hair", "Hair Accessories", 499, 650, 145, 40, "Trending", 4.8, 88, "🍷",
         "Plush micro-velvet bow in deep wine rose with cascading tails that frame ponytails and braids.",
         "Micro-velvet • Alligator grip clip • Rich wine hue"),
        ("BNB-HA-003", "Pearl & Crystal Twig Headband", "hair", "Hair Accessories", 599, 799, 180, 30, "Staff Pick", 5.0, 64, "👑",
         "Hand-wired glass pearls and sparkling crystals on a comfortable, pinch-free metal band.",
         "Glass seed pearls & crystals • Padded tips • Flexible fit"),
        ("BNB-HA-004", "Pastel Cloud Silk Scrunchie Trio", "hair", "Hair Accessories", 349, 499, 95, 60, "Pack of 3", 4.9, 210, "🌸",
         "Set of three creaseless silk scrunchies in Blush Pink, Dusty Rose, and Sage Cream.",
         "Pure silk satin • High-resilience core • Anti-breakage")
    ]

    # Seed all products idempotently so the catalog stays in sync with the current storefront mapping.
    for product in seed_products:
        cursor.execute('''
        INSERT INTO products (sku, title, category, cat_label, price, mrp, cost, stock, badge, rating, reviews_count, icon, description, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(sku) DO UPDATE SET
            title = excluded.title,
            category = excluded.category,
            cat_label = excluded.cat_label,
            price = excluded.price,
            mrp = excluded.mrp,
            cost = excluded.cost,
            stock = excluded.stock,
            badge = excluded.badge,
            rating = excluded.rating,
            reviews_count = excluded.reviews_count,
            icon = excluded.icon,
            description = excluded.description,
            details = excluded.details,
            is_active = 1
        ''', product)

    conn.commit()
    conn.close()
    print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    init_db()
