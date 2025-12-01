# sis2-datagathering
SIS 2 repository

# Arbuz.kz Scraper & ETL Pipeline with Airflow

This project automates data extraction from [Arbuz.kz](https://arbuz.kz/), cleans the extracted product information, and loads it into an SQLite database. Airflow is used to orchestrate the full ETL workflow.

---
## Functionality Overview

✔ Scrape product data (name, price, category, brand, availability, URL)  
✔ Clean and validate scraped data  
✔ Store results in SQLite database  
✔ Automated scheduling using Airflow  

---
# Table of Contents
1. [Project Description](#project-description)
2. [How It Works](#how-it-works)
3. [Installation & Setup](#installation--setup)
4. [How to Run Scraping](#how-to-run-scraping)
5. [Running Airflow](#running-airflow)
6. [Database Integration](#database-integration)
7. [Expected Output](#expected-output)
8. [Project Members](#project-members)
9. [Technical Topics](#technical-topics)
---

## Project Description
This application automatically gathers product details from the **Vegetables & Fruits category** on Arbuz.kz, including:

- Name  
- Price (₸ — Tenge)  
- Category  
- Brand (if available)  
- URL  
- Availability  
- Date & time of parsing  

The pipeline applies intelligent cleaning rules to remove duplicates, fix formatting, ensure correct data types, and only load valid records.

The final results are stored in a structured SQLite database for analysis.

---

## How It Works

| Stage | Description |
|-------|------------|
| Scraping | Selenium bot collects product links and product data |
| Cleaning | Invalid prices removed, missing names dropped, duplicates removed |
| Loading | Data inserted into `products` table in SQLite DB |
| Scheduling | Airflow automates daily scheduled scraping |

---

## Installation & Setup

```bash
pip install -r requirements.txt
````

Chrome WebDriver must be installed and match your Chrome version.

---

## How to Run Scraping

```python
from scraper import scrape_arbuz
from cleaner import clean_data
from loader import load_data

raw = scrape_arbuz(max_products=1000)
cleaned = clean_data(raw)
load_data(cleaned)
```

or simply:

```bash
python scraper.py
```

Database file will be created at:

```
data/parsing.db
```

---

## Running Airflow

Initialize:

```bash
airflow db init
```

Create admin user:

```bash
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

Start services:

```bash
airflow webserver -p 8080
airflow scheduler
```

Open UI:
[http://localhost:8080/](http://localhost:8080/)

Enable DAG `arbuz_scraper_dag` (if your DAG file is in `dags/` folder)

---

## Database Integration

Products are loaded into `products` table with fields:

| Column       | Type    | Description                     |
| ------------ | ------- | ------------------------------- |
| product_name | TEXT    | Clean product name              |
| product_url  | TEXT    | Unique product page URL         |
| price        | INTEGER | Product price                   |
| category     | TEXT    | Product category name           |
| brand        | TEXT    | Product brand                   |
| available    | INTEGER | 1 — available, 0 — out of stock |
| parse_date   | TEXT    | Timestamp of scraping           |

---

## Expected Output

Example logs:

```
Initial quantity(Before Cleaning): 1200
After Cleaning: 950
Loaded 950 records
```

Example record:

```json
{
  "product_name": "Ананас",
  "price": 1690,
  "category": "Фрукты",
  "brand": "Unknown",
  "available": true,
  "product_url": "...",
  "parse_date": "2025-01-15T14:32:10"
}
```

---

## Project Members

| Full Name | ID         | GitHub                                     |
| --------- | ---------- | ------------------------------------------ |
| Stelmakh Polina | 22B030588 | [Stelmakh](https://github.com/po133na) |
| Suanbekova Aisha | 22B030589 | [Suanbekova](https://github.com/Sunbekova) |
---

## Technical Topics

| Technical Stack |
|----------------|
| Selenium WebDriver |
| ETL Pipeline |
| Apache Airflow |
| Data Cleaning with Pandas |
| SQLite Database |
| Exception Handling & Logging |
| Headless Browser Automation |

---
[Back to Top](#arbuz.kz-scraper-&-etl-pipeline-with-airflow)