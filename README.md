# sis2-datagathering
SIS 2 repository

# Arbuz.kz Scraper & ETL Pipeline with Airflow

This repository contains an automated ETL pipeline for collecting product data from **Arbuz.kz**, cleaning it, and loading it into an SQLite database.
The project uses **Playwright** for scraping, **Pandas** for cleaning, **SQLite** for storage, and **Apache Airflow** for orchestration.

---

# Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [How It Works](#how-it-works)
4. [Installation & Setup](#installation--setup)
5. [Running the Scraper](#running-the-scraper)
6. [Database Initialization](#database-initialization)
7. [Airflow Pipeline](#airflow-pipeline)
8. [Database Schema](#database-schema)
9. [Expected Output](#expected-output)
10. [Project Members](#project-members)

---

## Project Overview

The ETL pipeline automatically gathers product data from several categories on **Arbuz.kz**, including:

- Name  
- Price (₸ — Tenge)  
- Category  
- Brand (if available)  
- URL  
- Availability  
- Scrape timestamp

The pipeline:

1. **Scrapes** product URLs and detailed product data from Arbuz.kz
2. **Cleans** the dataset using custom rules
3. **Loads** data into an SQLite database
4. **Schedules** daily execution via Airflow

---

## Features

✔ Automated scraping with **Playwright**
✔ Multi-category product extraction
✔ Data cleaning with Pandas
✔ SQLite storage
✔ Airflow DAG for full ETL pipeline
✔ Logging on every stage

---

## How It Works

| Stage | Description |
| -------------- | ---------------------------------------------------------------------- |
| Scraping  | collects product links & product details using Playwright |
| Cleaning   | removes duplicates, invalid entries, incorrect formats    |
| Loading    | inserts data into SQLite (`products` table)                |
| Scheduling | Airflow executes the ETL every day at 04:00 (DAG: `arbuz_pipeline`)    |

### Scraper Logic

* Visits **7 categories** (fruits, vegetables, greens, mushrooms, berries, fresh juices)
* Automatically scrolls, clicks “Load More”, and extracts all product cards
* Bypasses bot detection (user-agent override, disabling webdriver)
* Scrapes product details: name, price, category, brand, availability

---

## Installation & Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install Playwright drivers

```bash
playwright install
playwright install chromium
```

---

## Running the Scraper

### Option 1 — Run manually

```python
from scraper import scrape_arbuz
from cleaner import clean_data
from loader import load_data

raw = scrape_arbuz(max_products=150)
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

## Database Initialization

Before the first scrape, create the database and table:

```bash
python init_db.py
```

This creates:

```
data/parsing.db
```

With table:

```
products
```

---

## Airflow Pipeline

### Initialize Airflow

```bash
airflow db init
```

### Create admin user:

```bash
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

### Start services:

```bash
airflow webserver -p 8080
airflow scheduler
```

Open UI:
[http://localhost:8080/](http://localhost:8080/)

---

## Database Schema

`init_db.py` creates the following table:

| Column       | Type      | Description                         |
| ------------ | --------- | ----------------------------------- |
| id           | INTEGER   | Auto-increment primary key          |
| product_name | TEXT      | Clean product name                  |
| product_url  | TEXT      | Product page URL (unique)           |
| price        | INTEGER   | Price in Tenge                      |
| category     | TEXT      | Product category                    |
| brand        | TEXT      | Extracted brand (if exists)         |
| available    | INTEGER   | 1 = in stock, 0 = unavailable       |
| parse_date   | TEXT      | ISO timestamp                       |
| created_at   | TIMESTAMP | Auto-generated record creation time |

---

## Expected Output

Example logs:

```
scraping started from 7 categories
found 240 links in Фрукты
scraped total 150 products
cleaned rows: 138
Loaded records: 138
```

Example record:

```json
{
  "product_name": "Ананас",
  "price": 1690,
  "category": "Фрукты",
  "brand": "Unknown",
  "available": true,
  "product_url": "https://arbuz.kz/...",
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


[Back to Top](#arbuz.kz-scraper--etl-pipeline-with-airflow)