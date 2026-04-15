# E-commerce API Lakehouse 🛒

![Status: Paused](https://img.shields.io/badge/Status-Paused-yellow)

> ⚠️ **Project Status: On Hold**
> *Active development of this project is currently paused while I focus on other projects and learning milestones. You can review the current progress, architecture, and implemented features documented below. The existing codebase is fully functional.*

## 📌 Project Overview
This project implements an end-to-end, serverless Data Lakehouse architecture on AWS, designed to extract, transform, and analyze e-commerce data from the public MercadoLibre API. 

The primary focus of this repository is **robust API integration and data ingestion**. It showcases advanced techniques for consuming web APIs at scale, managing complex JSON responses, and preparing unstructured data for downstream Data Science and Analytics workflows.

## 🚀 Key Features
* **Resilient API Client:** Custom-built Python client utilizing `requests.Session()` for optimized connection pooling.
* **Smart Rate Limiting & Retries:** Implements exponential backoff to handle HTTP 429 (Too Many Requests) and 500+ server errors gracefully without dropping the pipeline.
* **Automated Pagination:** Dynamically handles API offsets and limits to extract complete category catalogs without memory bottlenecks.
* **Serverless Architecture Ready:** Codebase structured to be seamlessly deployed as AWS Lambda functions.
* **Medallion Architecture:** Designed to process data through Bronze (raw JSON), Silver (flattened/cleaned), and Gold (analytical schemas) layers using S3 and Athena.

## 📝 Implementation Details
* **`src/api_client/meli_client.py`**: Core API client class (`MeliClient`). Implements `requests.Session()` for connection pooling, environment variable loading for secure authentication (`MELI_ACCESS_TOKEN`), and a resilient `_make_request` method with exponential backoff for handling rate limits (429) and server anomalies (500+). Includes a flexible generic GET implementation (`get()`) for catalog targeting and built-in pagination handling for searches (`get_items_by_category`).
* **`src/extract/fetch_items.py`**: Extraction pipeline script targeting the Bronze Layer. Seeds product IDs from a local text file (`target_products.txt`) and orchestrates sequential product extractions using the generic `client.get()` method. Implements a robust one-by-one processing pattern with strategic rate-limiting pauses (`time.sleep`) to accommodate the lack of Multiget support for `/products` and respect API constraints, consolidating raw JSON payloads into dynamically timestamped files (e.g., `bronze_layer_smartphones_YYYYMMDD_HHMMSS.json`).

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Libraries:** `requests`, `pandas`, `boto3` (AWS SDK), `logging`
* **Target Infrastructure (AWS):** S3 (Data Lake), Lambda (Compute), Athena (SQL Engine), EventBridge (Orchestration)

## 🚧 Next Steps / Roadmap (On Hold)
- [x] **Phase 1: Robust API Ingestion** - Define architecture and implement a resilient API client with pagination and exponential backoff.
- [ ] **Phase 2: Infrastructure as Code (IaC)** - Define and provision the AWS Serverless architecture (S3, Lambda, EventBridge) using Terraform.
- [ ] **Phase 3: Hybrid Data Ingestion** - Complement API data with targeted Web Scraping to extract user Q&A and written reviews.
- [ ] **Phase 4: Machine Learning & NLP Integration** - Train time-series models for price volatility forecasting and deploy NLP models for sentiment analysis on unstructured text.

---
*Created as a professional portfolio project demonstrating modern Data Engineering and API consumption practices.*