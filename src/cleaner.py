import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)

def clean_data(raw_data):
    if not raw_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(raw_data)
    
    logging.info(f"Initial quantity(Before Cleaning): {len(df)}")
    
    df = df.drop_duplicates(subset=['product_url'])
    
    df = df.dropna(subset=['product_name', 'price'])
    
    df = df[df['price'] > 0]
    
    df['product_name'] = df['product_name'].str.strip()
    df['category'] = df['category'].str.strip()
    df['brand'] = df['brand'].str.strip()
    
    df['price'] = df['price'].astype(int)
    df['available'] = df['available'].astype(bool)
    
    logging.info(f"After Cleaning: {len(df)}")
    
    return df