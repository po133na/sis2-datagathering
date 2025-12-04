import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def load_data(df, db_path='data/parsing.db'):
    if df is None or df.empty:
        return 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO products (product_name, product_url, price, category, brand, available, parse_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row['product_name'],
                row['product_url'],
                int(row['price']),
                row['category'],
                row['brand'],
                1 if row['available'] else 0,
                row['parse_date']
            ))
        
        conn.commit()
        logging.info(f"Loaded records: {len(df)}")
        return len(df)
    except Exception as e:
        logging.error(f"error: {e}")
        return 0
    finally:
        conn.close()
