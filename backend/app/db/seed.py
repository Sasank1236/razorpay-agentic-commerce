import uuid
import random
import datetime
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.models import (
    User, Product, Inventory, Cart, CartItem, Order, OrderItem,
    Payment, SearchEvent, ProductView, Recommendation, AgentAction, Campaign
)

def seed_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        print("[SEED] Seeding Users...")
        customer_user = User(
            id="user_customer_01",
            name="Rahul Sharma",
            email="rahul.sharma@example.com",
            role="customer",
            preferences={"preferred_categories": ["Audio", "Accessories"], "avg_budget": 5000}
        )
        merchant_user = User(
            id="user_merchant_01",
            name="Apex Tech Merchant",
            email="merchant@razorbuy.com",
            role="merchant",
            preferences={"store_name": "Apex Electronics & Gear"}
        )
        db.add_all([customer_user, merchant_user])
        db.commit()

        print("[SEED] Seeding Products (100+ items)...")
        categories_data = [
            {
                "category": "Audio",
                "items": [
                    ("SoundMax Pro Wireless Headphones", "Premium noise-canceling wireless headphones with crystal clear call quality and 38-hour battery.", 4499.0, 5999.0, 4.6, 128, {"battery": "38h", "mic": "dual-beamforming", "anc": True, "weight": "220g"}, ["bestseller", "calls", "long-battery", "audio"], "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
                    ("AudioPhonic H50", "High-fidelity over-ear Bluetooth headphones with deep bass boost and quick charge.", 3299.0, 4299.0, 4.3, 85, {"battery": "30h", "mic": "standard", "anc": False, "weight": "240g"}, ["budget", "bass", "audio"], "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=500"),
                    ("SonicPod ANC Earbuds", "True wireless earbuds with active noise cancellation and IPX5 water resistance.", 4999.0, 6999.0, 4.5, 210, {"battery": "28h total", "mic": "quad-mic", "anc": True, "waterproof": "IPX5"}, ["earbuds", "anc", "sports"], "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500"),
                    ("Boat WaveRider 450", "On-ear wireless headphones with soft cushion padding and 15-hour playback.", 1499.0, 2499.0, 4.1, 340, {"battery": "15h", "mic": "basic", "anc": False}, ["budget", "entry-level"], "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500"),
                    ("Sony WH-1000XM5 Studio", "Industry-leading noise canceling headphones with Auto NC Optimizer and 30-hour battery.", 29990.0, 34990.0, 4.8, 512, {"battery": "30h", "mic": "8-mic system", "anc": True, "codec": "LDAC"}, ["flagship", "premium", "anc"], "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500"),
                    ("JBL Live 660NC", "Wireless over-ear noise canceling headphones with signature JBL sound and multi-point connection.", 8999.0, 11999.0, 4.4, 180, {"battery": "50h", "mic": "dual", "anc": True}, ["jbl", "long-battery"], "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500"),
                    ("Sennheiser Accentum", "Audiophile-grade wireless acoustics with 50-hour battery life and hybrid ANC.", 12990.0, 14990.0, 4.6, 94, {"battery": "50h", "mic": "hd-voice", "anc": True}, ["audiophile", "sennheiser"], "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=500"),
                    ("Realme Buds Air 5 Pro", "Dual driver TWS with 50dB active noise cancellation and spatial audio.", 4999.0, 5999.0, 4.5, 410, {"battery": "40h", "mic": "6-mic", "anc": True}, ["value-king", "tws"], "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=500"),
                    ("Bose QuietComfort Ultra", "World-class spatial audio headphones with custom tuned sound and supreme comfort.", 35900.0, 39900.0, 4.9, 150, {"battery": "24h", "mic": "studio-grade", "anc": True}, ["bose", "ultra-premium"], "https://images.unsplash.com/photo-1545127398-14699f92334b?w=500"),
                    ("Marshall Major IV", "Iconic wireless headphones with 80+ hours of Bluetooth playback and wireless charging.", 11999.0, 14999.0, 4.7, 230, {"battery": "80h", "mic": "good", "anc": False}, ["vintage", "battery-beast"], "https://images.unsplash.com/photo-1590658006821-04f4008d5717?w=500")
                ]
            },
            {
                "category": "Wearables",
                "items": [
                    ("PulseFit Pro Smartwatch", "AMOLED display smartwatch with heart rate, SpO2, GPS, and Bluetooth calling.", 3999.0, 5999.0, 4.4, 215, {"display": "1.43 AMOLED", "battery": "7 days", "gps": True, "waterproof": "IP68"}, ["fitness", "calling", "amoled"], "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500"),
                    ("Apex Ultra Watch GS", "Rugged outdoor smartwatch with dual-frequency GPS and titanium alloy casing.", 8999.0, 11999.0, 4.7, 95, {"display": "1.5 AMOLED", "battery": "14 days", "gps": True, "casing": "Titanium"}, ["outdoor", "rugged", "gps"], "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=500"),
                    ("Noise ColorFit Icon 3", "Budget Bluetooth calling watch with metallic finish and 100+ sports modes.", 1799.0, 2999.0, 4.2, 530, {"display": "1.8 HD", "battery": "5 days", "gps": False}, ["budget", "calling"], "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
                    ("Apple Watch SE 2nd Gen", "Essential fitness and health features with Crash Detection and Retina display.", 24900.0, 29900.0, 4.8, 620, {"display": "Retina OLED", "battery": "18h", "ecosystem": "iOS"}, ["apple", "premium"], "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=500"),
                    ("Samsung Galaxy Watch 6", "Advanced sleep tracking, personalized HR zones, and sapphire crystal glass.", 19999.0, 24999.0, 4.6, 280, {"display": "Super AMOLED", "battery": "40h", "os": "WearOS"}, ["samsung", "wearos"], "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
                    ("Fire-Boltt Phoenix Pro", "1.39 inch Bluetooth calling smartwatch with AI voice assistant and metal body.", 1499.0, 2499.0, 4.1, 780, {"display": "1.39 TFT", "battery": "7 days"}, ["entry", "budget"], "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=500"),
                    ("Fitbit Charge 6", "Advanced fitness tracker with built-in GPS, EDA sensor, and 7-day battery.", 14999.0, 16999.0, 4.3, 110, {"display": "OLED Color", "battery": "7 days", "gps": True}, ["fitbit", "health"], "https://images.unsplash.com/photo-1576243345690-4e4b79b63284?w=500"),
                    ("Garmin Forerunner 265", "Running smartwatch with vivid AMOLED display and training metrics.", 45990.0, 49990.0, 4.9, 88, {"display": "AMOLED", "battery": "13 days", "gps": True}, ["garmin", "runner-pro"], "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=500"),
                    ("Titan Talk S Smartwatch", "Premium designer smartwatch with 1.78 AMOLED display and BT calling.", 5995.0, 7995.0, 4.4, 140, {"display": "1.78 AMOLED", "battery": "5 days"}, ["titan", "lifestyle"], "https://images.unsplash.com/photo-1539185441755-769473a23570?w=500"),
                    ("Amazfit GTR 4", "Dual-band circular smartwatch with 150+ sports modes and Alexa built-in.", 16999.0, 19999.0, 4.6, 310, {"display": "1.43 HD AMOLED", "battery": "14 days", "gps": True}, ["amazfit", "battery-king"], "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=500")
                ]
            },
            {
                "category": "Accessories",
                "items": [
                    ("Logitech MX Master 3S", "Performance wireless ergonomics mouse with 8K DPI tracking and quiet clicks.", 8995.0, 10995.0, 4.8, 430, {"dpi": "8000", "battery": "70 days", "connectivity": "Bluetooth + Bolt"}, ["mouse", "productivity", "logitech"], "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500"),
                    ("Keychron K2 Pro Mechanical Keyboard", "QMK/VIA wireless custom mechanical keyboard with hot-swappable switches.", 9999.0, 12999.0, 4.7, 190, {"switches": "Gateron Brown", "layout": "75%", "rgb": True}, ["keyboard", "mechanical", "keychron"], "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500"),
                    ("Anker 737 Power Bank (24,000mAh)", "140W ultra-powerful 3-port portable charger with smart digital display.", 11999.0, 14999.0, 4.9, 310, {"capacity": "24000mAh", "output": "140W PD3.1"}, ["powerbank", "fast-charging", "anker"], "https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=500"),
                    ("Razer DeathAdder V3 Pro", "Ultra-lightweight wireless esports gaming mouse with Focus Pro 30K sensor.", 12499.0, 14999.0, 4.7, 160, {"weight": "63g", "sensor": "30K DPI", "wireless": True}, ["gaming", "razer", "lightweight"], "https://images.unsplash.com/photo-1527814050087-3793815479db?w=500"),
                    ("SanDisk 1TB Extreme Portable SSD", "High-speed NVMe solid state drive with up to 1050MB/s read speeds.", 8499.0, 11999.0, 4.6, 890, {"speed": "1050MB/s", "durability": "IP65 water/dust"}, ["storage", "ssd", "sandisk"], "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500"),
                    ("HyperX QuadCast S RGB Mic", "Full-featured USB condenser microphone with anti-vibration shock mount.", 13490.0, 16490.0, 4.8, 270, {"polar_pattern": "4 patterns", "rgb": True, "tap_to_mute": True}, ["mic", "streaming", "hyperx"], "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500"),
                    ("Baseus 65W GaN Fast Charger", "Compact 3-port GaN wall charger for laptops, phones, and tablets.", 2499.0, 3999.0, 4.4, 450, {"ports": "2x USB-C + 1x USB-A", "output": "65W"}, ["charger", "gan", "travel"], "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500"),
                    ("Elgato Stream Deck MK.2", "15 customizable LCD keys for controlling apps and broadcasting tools.", 14999.0, 16999.0, 4.9, 140, {"keys": "15 LCD", "interface": "USB 2.0"}, ["elgato", "creator"], "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=500"),
                    ("Portronics Laptop Cooling Pad", "Dual fan laptop stand with RGB lighting and 6 height adjustments.", 1299.0, 1999.0, 4.1, 620, {"fans": "2x 120mm", "usb": "2 ports"}, ["cooling", "budget"], "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500"),
                    ("Verbatim 7-in-1 USB-C Hub", "4K HDMI, 100W Power Delivery, SD Card Reader, and 3x USB 3.0 ports.", 2199.0, 3499.0, 4.3, 380, {"ports": "7 ports", "hdmi": "4K 30Hz"}, ["adapter", "usb-c"], "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500")
                ]
            },
            {
                "category": "Laptops",
                "items": [
                    ("Apple MacBook Air M2", "Thinnest 13.6-inch Liquid Retina display laptop with M2 chip, 8GB RAM, 256GB SSD.", 89900.0, 99900.0, 4.9, 810, {"cpu": "Apple M2", "ram": "8GB", "ssd": "256GB", "battery": "18h"}, ["apple", "macbook", "m2", "thin"], "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500"),
                    ("Dell XPS 13 Plus", "13.4 inch FHD+ InfinityEdge touch laptop with Intel i7 13th Gen, 16GB RAM, 512GB SSD.", 134990.0, 149990.0, 4.6, 120, {"cpu": "Intel i7-1360P", "ram": "16GB", "ssd": "512GB"}, ["dell", "xps", "premium"], "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500"),
                    ("Lenovo Legion Slim 5", "AMD Ryzen 7 7840HS gaming laptop with RTX 4060, 16GB DDR5, 1TB SSD.", 109990.0, 124990.0, 4.7, 240, {"cpu": "Ryzen 7 7840HS", "gpu": "RTX 4060 8GB", "ram": "16GB"}, ["lenovo", "gaming", "rtx4060"], "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500"),
                    ("HP Pavilion 14 Aero", "Ultra-lightweight 1kg laptop with AMD Ryzen 5 7535U, 16GB RAM, 512GB SSD.", 54990.0, 64990.0, 4.4, 310, {"cpu": "Ryzen 5 7535U", "ram": "16GB", "weight": "1.0kg"}, ["hp", "lightweight", "budget-work"], "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500"),
                    ("ASUS ROG Zephyrus G14", "Compact 14-inch QHD 165Hz gaming laptop with Ryzen 9, RTX 4070, 16GB, 1TB.", 164990.0, 184990.0, 4.8, 190, {"cpu": "Ryzen 9 7940HS", "gpu": "RTX 4070", "display": "14 QHD+ 165Hz"}, ["asus", "rog", "flagship-gaming"], "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500")
                ]
            },
            {
                "category": "Smart Home",
                "items": [
                    ("Amazon Echo Dot 5th Gen", "Smart speaker with Alexa, deeper bass, vibrant sound, and motion sensor.", 4499.0, 5499.0, 4.5, 950, {"voice_assistant": "Alexa", "wifi": "Dual Band"}, ["alexa", "smart-speaker"], "https://images.unsplash.com/photo-1543512214-318c7553f230?w=500"),
                    ("Google Nest Mini 2nd Gen", "Wall-mountable smart speaker with Google Assistant and room-filling sound.", 3499.0, 4499.0, 4.3, 720, {"voice_assistant": "Google Assistant"}, ["google", "nest"], "https://images.unsplash.com/photo-1507646298591-24757e6985d8?w=500"),
                    ("Philips Hue Smart Starter Kit", "3 E27 color smart bulbs + Bridge for wireless smart home ambiance.", 9999.0, 12999.0, 4.7, 210, {"color": "16 million colors", "app": "Philips Hue"}, ["lighting", "philips", "rgb"], "https://images.unsplash.com/photo-1550985616-10810253b84d?w=500"),
                    ("Wipro 16A Smart Plug with Energy Meter", "Control heavy appliances like AC and Geyser remotely via Wipro Next App.", 999.0, 1999.0, 4.2, 1100, {"power": "16A", "energy_monitoring": True}, ["smart-plug", "wipro"], "https://images.unsplash.com/photo-1558002038-1055907df827?w=500"),
                    ("TP-Link Tapo C200 Security Camera", "Pan/Tilt home security Wi-Fi camera with 1080p crystal night vision.", 1899.0, 2999.0, 4.4, 1540, {"resolution": "1080p", "rotation": "360 deg pan"}, ["security", "camera", "tplink"], "https://images.unsplash.com/photo-1557324232-b8917d3c3dcb?w=500")
                ]
            }
        ]

        products_list = []
        inventory_list = []

        idx = 1
        for cat_obj in categories_data:
            cat_name = cat_obj["category"]
            for item in cat_obj["items"]:
                p_id = f"prod_{idx:03d}"
                prod = Product(
                    id=p_id,
                    title=item[0],
                    description=item[1],
                    category=cat_name,
                    brand=item[0].split()[0],
                    price=item[2],
                    original_price=item[3],
                    rating=item[4],
                    review_count=item[5],
                    specs=item[6],
                    tags=item[7],
                    image_url=item[8]
                )
                inv = Inventory(
                    id=f"inv_{idx:03d}",
                    product_id=p_id,
                    stock_quantity=random.randint(15, 120),
                    reserved_quantity=random.randint(0, 5)
                )
                products_list.append(prod)
                inventory_list.append(inv)
                idx += 1

        brands = ["TechCraft", "Vibe", "HyperSonic", "Volt", "Aero", "Pulse", "Zenith", "Quantum", "Nexus", "Vertex"]
        sub_categories = {
            "Audio": ("Wireless Earbuds", "Bluetooth Speaker", "Gaming Headset", "Neckband"),
            "Wearables": ("Smart Band", "Sports Watch", "Health Tracker"),
            "Accessories": ("Fast Cable", "Mousepad RGB", "Laptop Sleeve", "Phone Mount"),
            "Laptops": ("Slim Ultrabook", "Convertible 2-in-1"),
            "Smart Home": ("Smart Strip", "Motion Sensor", "Doorbell Cam")
        }

        while idx <= 105:
            cat_name = random.choice(list(sub_categories.keys()))
            sub_type = random.choice(sub_categories[cat_name])
            brand = random.choice(brands)
            title = f"{brand} {sub_type} X{idx}"
            price = float(random.randint(12, 450) * 100 - 1)
            orig_price = round(price * random.uniform(1.15, 1.4), -1) + 9
            rating = round(random.uniform(3.9, 4.9), 1)
            reviews = random.randint(20, 600)
            p_id = f"prod_{idx:03d}"
            
            prod = Product(
                id=p_id,
                title=title,
                description=f"High performance {sub_type.lower()} by {brand} designed for everyday reliability and seamless connectivity.",
                category=cat_name,
                brand=brand,
                price=price,
                original_price=orig_price,
                rating=rating,
                review_count=reviews,
                specs={"connectivity": "Bluetooth 5.3", "warranty": "1 Year", "color": "Matte Black"},
                tags=[cat_name.lower(), sub_type.lower().replace(" ", "-"), "featured"],
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
            )
            inv = Inventory(
                id=f"inv_{idx:03d}",
                product_id=p_id,
                stock_quantity=random.randint(10, 80),
                reserved_quantity=0
            )
            products_list.append(prod)
            inventory_list.append(inv)
            idx += 1

        db.add_all(products_list)
        db.add_all(inventory_list)
        db.commit()

        print("[SEED] Seeding Analytics Data (Searches, Views, Carts, Orders)...")
        sample_queries = [
            "wireless headphones under 5000 for calls",
            "best smartwatches with amoled display and calling",
            "gaming mouse under 10000 with silent clicks",
            "macbook air m2 256gb best price",
            "bluetooth speaker with long battery life",
            "noise canceling earbuds under 5k"
        ]

        search_events = []
        for i in range(40):
            q = random.choice(sample_queries)
            s_evt = SearchEvent(
                id=f"se_{i:03d}",
                user_id="user_customer_01",
                query=q,
                extracted_intent={"category": "Audio" if "headphones" in q or "earbuds" in q else "Wearables", "max_price": 5000},
                results_count=random.randint(4, 25),
                converted_to_cart=random.choice([True, False, False]),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=random.randint(1, 168))
            )
            search_events.append(s_evt)
        db.add_all(search_events)

        product_views = []
        for i in range(60):
            p = random.choice(products_list)
            pv = ProductView(
                id=f"pv_{i:03d}",
                user_id="user_customer_01",
                product_id=p.id,
                duration_seconds=random.randint(10, 180),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=random.randint(1, 168))
            )
            product_views.append(pv)
        db.add_all(product_views)

        abandoned_cart = Cart(
            id="cart_abandoned_01",
            user_id="user_customer_01",
            status="abandoned",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=14)
        )
        db.add(abandoned_cart)
        db.commit()

        cart_items_abandoned = [
            CartItem(id="ci_ab_01", cart_id="cart_abandoned_01", product_id="prod_001", quantity=1, unit_price=4499.0),
            CartItem(id="ci_ab_02", cart_id="cart_abandoned_01", product_id="prod_011", quantity=1, unit_price=8995.0)
        ]
        db.add_all(cart_items_abandoned)

        past_order = Order(
            id="ord_past_01",
            user_id="user_customer_01",
            total_amount=3999.0,
            currency="INR",
            status="paid",
            razorpay_order_id="order_dummy_razorpay_101",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        )
        db.add(past_order)
        db.commit()

        order_item = OrderItem(
            id="oi_past_01",
            order_id="ord_past_01",
            product_id="prod_011",
            quantity=1,
            price=3999.0
        )
        payment_record = Payment(
            id="pay_past_01",
            order_id="ord_past_01",
            razorpay_order_id="order_dummy_razorpay_101",
            razorpay_payment_id="pay_dummy_razorpay_201",
            razorpay_signature="dummy_signature_verified",
            amount=3999.0,
            status="captured",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        )
        db.add_all([order_item, payment_record])

        campaign = Campaign(
            id="camp_01",
            title="Headphone Recovery Discount",
            description="Promote SoundMax Pro with 5% instant discount to high-intent shoppers searching under ₹5,000.",
            target_segment="Headphone Searchers < ₹5,000",
            discount_percent=5.0,
            target_product_id="prod_001",
            status="active",
            metrics={"impressions": 142, "conversions": 19, "revenue": 85481.0}
        )
        db.add(campaign)

        agent_action = AgentAction(
            id="action_demo_01",
            agent_type="customer",
            action_name="search_and_recommend",
            input_params={"query": "wireless headphones under 5000 for calls"},
            output_summary={"recommended_product": "SoundMax Pro Wireless Headphones", "score": 94.5},
            execution_time_ms=420,
            timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        )
        db.add(agent_action)

        db.commit()
        print("[SUCCESS] Database successfully seeded with 105 products, inventory, users, carts, orders, and analytics!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
