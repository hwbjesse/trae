# -*- coding: utf-8 -*-
from app import app, db

with app.app_context():
    conn = db.engine.connect()
    try:
        conn.execute(db.text("UPDATE customer SET created_at = DATE(created_at)"))
        conn.execute(db.text("UPDATE customer SET updated_at = DATE(updated_at)"))
        conn.commit()
        print("[OK] Date migration completed")
    except Exception as e:
        print(f"[SKIP] Migration skipped: {e}")
    conn.close()
    print("[DONE] Database migration finished!")