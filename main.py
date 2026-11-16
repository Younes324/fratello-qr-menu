import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Fratello QR Ordering")

def init_db():
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            items TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            ingredients TEXT DEFAULT '',
            variants TEXT DEFAULT '',
            compatible_with TEXT DEFAULT '',
            is_available INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'unread'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER DEFAULT NULL,
            table_number INTEGER NOT NULL,
            target_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            tags TEXT DEFAULT '',
            comment TEXT DEFAULT '',
            is_verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM menu_items")
    if cursor.fetchone()[0] == 0:
        default_items = [
            # PIZZAS
            ("Pizzas", "Marguerite", 450, "S.tomate. Gruyère. Mozzarella. Olives.", "Mini:300,Nrml:450,Mega:1500,Turk:500", "", 1),
            ("Pizzas", "Neptun", 600, "S.tomate. Thon. gruyère. Mozzarella. Olives.", "Mini:350,Nrml:600,Mega:1800,Turk:650", "", 1),
            ("Pizzas", "Forestière", 600, "S.tomate. Champignons frais. Gruyère. Mozzarella. Olives.", "Mini:350,Nrml:600,Mega:1800,Turk:650", "", 1),
            ("Pizzas", "Mexicaine", 800, "S.tomate. Poulet mexicain. Poivrons. Gruyère. Mozzarella. Olives.", "Mini:450,Nrml:800,Mega:2400,Turk:850", "", 1),
            ("Pizzas", "Sharapova", 800, "S.tomate. Peperoni. Merguez. Gruyère. Mozzarella. Olives.", "Mini:450,Nrml:800,Mega:2400,Turk:850", "", 1),
            ("Pizzas", "Canibale", 800, "S.blanch. Poulet. Gruyère. Mozzarella. Olives.", "Mini:400,Nrml:800,Mega:2400,Turk:850", "", 1),
            ("Pizzas", "Croustillant", 700, "S.blanch. Poulet pané. Gruyère. Mozzarella. Olives.", "Mini:400,Nrml:700,Mega:2100,Turk:750", "", 1),
            ("Pizzas", "Algerienne", 600, "S.tomate. Poulet hachée. Gruyère. Mozzarella. Olives.", "Mini:400,Nrml:600,Mega:1800,Turk:650", "", 1),
            ("Pizzas", "Végétarienne", 650, "S.tomate. Poivrons. Champignons frais. Oignions. Gruyère. Mozzarella. Olives.", "Mini:450,Nrml:650,Mega:1950,Turk:700", "", 1),
            ("Pizzas", "Vegas", 700, "S.tomate. VH veaux. Gruyère. Mozzarella. Olives.", "Mini:400,Nrml:700,Mega:2100,Turk:750", "", 1),
            ("Pizzas", "Diavola", 750, "S.tomate. Chicken chika. Poivrons. Gruyère. Mozzarella. Olives.", "Mini:450,Nrml:750,Mega:2250,Turk:800", "", 1),
            ("Pizzas", "4 Fromages", 750, "S.tomate. Camembert. Fumé. Gruyère. Mozzarella. Olives.", "Mini:450,Nrml:750,Mega:2250,Turk:800", "", 1),
            ("Pizzas", "Delicieuse", 800, "S.blanch. Poulet. Fume. Dind fume. Gruyère. Mozzarella. Olives.", "Mini:450,Nrml:800,Mega:2400,Turk:850", "", 1),
            ("Pizzas", "Frattelo", 1000, "Choix de chef", "Mini:500,Nrml:1000,Mega:2800,Turk:1000", "", 1),

            # SANDWICHS
            ("Sandwichs", "Sandwich Classic", 200, "Sauce maison. Poulet hachée. Frites. salade. tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Avide", 300, "Sauce maison. Steak haché. Oeufs. Slice. Frites. salade. Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Combo", 450, "Sauce maison. Double steak haché. Dind fumé. Oeufs. Slice Frites. salade Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Galata Saray", 500, "Sauce maison. Steak haché. Merguez. Frites. salade. Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Tartar", 400, "Sauce maison. Escalope jaune. Frites. salade Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Mexicain", 450, "Sauce maison. Escalope mexicain. Frites. salade. Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Antalya", 500, "Sauce maison. Escalope 3 fromages. Frites.", "", "", 1),
            ("Sandwichs", "Sandwich Crousstillant", 450, "Sauce maison. Escalope pané. Frites. Salade. Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Mixte", 550, "Sauce maison. Steak haché. Escalope. Frites. Salade. Tomate.", "", "", 1),
            ("Sandwichs", "Sandwich Fratello", 600, "Choix de chef", "", "", 1),

            # TACOS
            ("Tacos", "Tacos Avide", 400, "Sauce maison. Steak haché. Oeufs. Slice. Frites. salade. Tomate.", "", "", 1),
            ("Tacos", "Tacos Combo", 600, "Sauce maison. Double steak haché. Dind fumé. Oeufs. Slice Frites. salade Tomate.", "", "", 1),
            ("Tacos", "Tacos Galata Saray", 600, "Sauce maison. Steak haché. Merguez. Frites. salade. Tomate.", "", "", 1),
            ("Tacos", "Tacos Tartar", 500, "Sauce maison. Escalope jaune. Frites. salade Tomate.", "", "", 1),
            ("Tacos", "Tacos Mexicain", 550, "Sauce maison. Escalope mexicain. Frites. salade. Tomate.", "", "", 1),
            ("Tacos", "Tacos Antalya", 600, "Sauce maison. Escalope 3 fromages. Frites.", "", "", 1),
            ("Tacos", "Tacos Crousstillant", 550, "Sauce maison. Escalope pané. Frites. Salade. Tomate.", "", "", 1),
            ("Tacos", "Tacos Mixte", 650, "Sauce maison. Steak haché. Escalope. Frites. Salade. Tomate.", "", "", 1),
            ("Tacos", "Tacos Fratello", 700, "Choix de chef", "", "", 1),

            # BURGERS
            ("Burgers", "Burger Cheese", 200, "Sauce maison. Poulet hachée. Slice. Salade. Tomate.", "", "", 1),
            ("Burgers", "Burger Le Steak", 280, "Sauce maison. Steak haché. Slice. Salade. Tomate.", "", "", 1),
            ("Burgers", "Burger Mushroom", 350, "Sauce maison. Steak haché. Oeufs. Dind fumé. Slice. Salade. Tomate.", "", "", 1),
            ("Burgers", "Burger Croustillant", 400, "Sauce maison. Escalop pané. Salade. tomate.", "", "", 1),
            ("Burgers", "Burger Rolo", 450, "Sauce maison. Double steak haché. Oeufs. Dind fumé. Slice. Salade.", "", "", 1),

            # BOWLS
            ("Bowls", "Bowl 3 Pieces", 500, "Escalop panne. Frites. Sauce blanche.", "", "", 1),
            ("Bowls", "Bowl 6 Pieces", 800, "Escalop panne. Frites. Sauce blanche.", "", "", 1),
            ("Bowls", "Bowl 9 Pieces", 1100, "Escalop panne. Frites. Sauce blanche.", "", "", 1),
            ("Bowls", "Bowl Mexicain", 500, "Escalope mexicain. Frites. Sauce blanche.", "", "", 1),
            ("Bowls", "Bowl Indien", 500, "", "", "", 1),
            ("Bowls", "Bowl Veau", 600, "", "", "", 1),
            ("Bowls", "Bowl Fratello", 800, "Choix de chef", "", "", 1),

            # SALADES & CALZON
            ("Salades", "Salade Cesar", 500, "", "", "", 1),
            ("Salades", "Salade au Thon", 400, "", "", "", 1),
            ("Salades", "Salade Fratello", 600, "Choix de chef", "", "", 1),
            ("Calzon", "Calzon Antalya", 850, "", "", "", 1),
            ("Calzon", "Calzon Mix", 1000, "", "", "", 1),

            # SUPPLEMENTS
            ("Suppléments", "Barquette de Frites", 100, "", "", "ALL", 1),
            ("Suppléments", "Bordure Fromage", 100, "", "", "Pizzas", 1),
            ("Suppléments", "Sauce Blanche", 100, "", "", "Pizzas", 1),
            ("Suppléments", "Champignons", 100, "", "", "Pizzas", 1),
            ("Suppléments", "Camembert", 100, "", "", "Pizzas,Sandwichs", 1),
            ("Suppléments", "Fumé", 100, "", "", "Pizzas,Sandwichs", 1),
            ("Suppléments", "Viande Hachée / Poulet", 200, "", "", "Sandwichs", 1)
        ]
        cursor.executemany(
            "INSERT INTO menu_items (category, name, price, ingredients, variants, compatible_with, is_available) VALUES (?, ?, ?, ?, ?, ?, ?)",
            default_items
        )

    conn.commit()
    conn.close()

init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get_customer_page(): return FileResponse("static/customer.html")

@app.get("/cashier")
def get_cashier_page(): return FileResponse("static/cashier.html")

@app.get("/kitchen")
def get_kitchen_page(): return FileResponse("static/kitchen.html")

class OrderCreate(BaseModel):
    table_number: int
    items: str
    total_price: float

class OrderStatusUpdate(BaseModel):
    status: str

class MenuAvailabilityUpdate(BaseModel):
    is_available: int

class SingleReviewInput(BaseModel):
    target_type: str
    item_name: str
    rating: int
    tags: Optional[str] = ""
    comment: Optional[str] = ""

class BatchReviewCreate(BaseModel):
    table_number: int
    order_id: Optional[int] = None
    reviews: List[SingleReviewInput]

@app.get("/api/menu")
def get_available_menu():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_items WHERE is_available = 1 ORDER BY id ASC")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

@app.get("/api/menu/all")
def get_all_menu():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_items ORDER BY id ASC")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

@app.patch("/api/menu/{item_id}/availability")
def toggle_menu_item(item_id: int, update: MenuAvailabilityUpdate):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE menu_items SET is_available = ? WHERE id = ?", (update.is_available, item_id))
    conn.commit()
    conn.close()
    return {"message": "Updated"}

@app.post("/api/tables/seated/{table_number}")
def notify_table_seated(table_number: int):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (table_number, message, status) VALUES (?, ?, 'unread')",
                   (table_number, f"👋 Table {table_number} vient de s'installer !"))
    conn.commit()
    conn.close()
    return {"message": "Notified"}

@app.post("/api/tables/call/{table_number}")
def call_waiter(table_number: int):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (table_number, message, status) VALUES (?, ?, 'unread')",
                   (table_number, f"🛎️ Table {table_number} demande un serveur !"))
    conn.commit()
    conn.close()
    return {"message": "Notified"}

@app.get("/api/notifications")
def get_notifications():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications WHERE status = 'unread' ORDER BY id DESC")
    notifs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notifs

@app.patch("/api/notifications/{notif_id}/dismiss")
def dismiss_notification(notif_id: int):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET status = 'read' WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()
    return {"message": "Dismissed"}

@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (table_number, items, total_price, status) VALUES (?, ?, ?, 'pending')",
                   (order.table_number, order.items, order.total_price))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"message": "Order created", "order_id": order_id}

@app.get("/api/orders/pending")
def get_pending_orders():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status = 'pending' ORDER BY id ASC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

@app.get("/api/orders/kitchen")
def get_kitchen_orders():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status = 'approved' ORDER BY id ASC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

@app.get("/api/orders/{order_id}")
def get_order_status(order_id: int):
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Not found")
    return dict(row)

@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: int, update: OrderStatusUpdate):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (update.status, order_id))
    conn.commit()
    conn.close()
    return {"message": "Updated"}

@app.delete("/api/orders/{order_id}")
def cancel_order(order_id: int):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ? AND status = 'pending'", (order_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if not success: raise HTTPException(status_code=400, detail="Cannot cancel")
    return {"message": "Cancelled"}

# --- SMART CUSTOMER REVIEWS ENDPOINTS ---
@app.get("/api/reviews/summary")
def get_reviews_summary():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT ROUND(AVG(rating), 1) as avg_rating, COUNT(*) as total_count FROM reviews")
    overall_row = cursor.fetchone()
    overall = {
        "avg": overall_row["avg_rating"] or 0,
        "count": overall_row["total_count"] or 0
    }

    cursor.execute("""
        SELECT item_name, ROUND(AVG(rating), 1) as avg_rating, COUNT(*) as count
        FROM reviews
        WHERE target_type = 'item'
        GROUP BY item_name
    """)
    items_map = {}
    for row in cursor.fetchall():
        items_map[row["item_name"]] = {
            "avg": row["avg_rating"],
            "count": row["count"]
        }

    cursor.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 40")
    recent = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {"overall": overall, "items": items_map, "recent": recent}

@app.post("/api/reviews/batch", status_code=201)
def submit_batch_reviews(payload: BatchReviewCreate):
    if not payload.reviews:
        raise HTTPException(status_code=400, detail="Aucun avis envoyé")

    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()

    if payload.order_id is not None:
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE order_id = ?", (payload.order_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            raise HTTPException(status_code=400, detail="Cette commande a déjà été évaluée.")

    is_verified = 1 if payload.order_id is not None else 0
    low_ratings = []

    for r in payload.reviews:
        rating = max(1, min(5, int(r.rating)))
        clean_comment = (r.comment or "").strip()
        clean_tags = (r.tags or "").strip()
        cursor.execute(
            """INSERT INTO reviews (order_id, table_number, target_type, item_name, rating, tags, comment, is_verified)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (payload.order_id, payload.table_number, r.target_type, r.item_name, rating, clean_tags, clean_comment, is_verified)
        )
        if rating <= 2:
            low_ratings.append((r.item_name, rating, clean_comment))

    # Smart escalation: alert cashier immediately if any rating is 1 or 2 stars
    for item_name, rating, comment in low_ratings:
        note = f" — « {comment} »" if comment else ""
        cursor.execute(
            "INSERT INTO notifications (table_number, message, status) VALUES (?, ?, 'unread')",
            (payload.table_number, f"⚠️ Avis critique ({rating}★) Table {payload.table_number} sur {item_name}{note}")
        )

    conn.commit()
    conn.close()
    return {"message": "Merci pour votre avis !"}

@app.delete("/api/reviews/{review_id}")
def delete_review(review_id: int):
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted"}
