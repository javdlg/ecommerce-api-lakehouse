# E-commerce API Lakehouse 🛒

## 📌 Project Overview
This project implements an end-to-end, serverless Data Lakehouse architecture on AWS, designed to extract, transform, and analyze e-commerce data from the public MercadoLibre API. 

The primary focus of this repository is **robust API integration and data ingestion**. It showcases advanced techniques for consuming web APIs at scale, managing complex JSON responses, and preparing unstructured data for downstream Data Science and Analytics workflows.

## 🚀 Key Features
* **Resilient API Client:** Custom-built Python client utilizing `requests.Session()` for optimized connection pooling.
* **Smart Rate Limiting & Retries:** Implements exponential backoff to handle HTTP 429 (Too Many Requests) and 500+ server errors gracefully without dropping the pipeline.
* **Automated Pagination:** Dynamically handles API offsets and limits to extract complete category catalogs without memory bottlenecks.
* **Serverless Architecture Ready:** Codebase structured to be seamlessly deployed as AWS Lambda functions.
* **Medallion Architecture:** Designed to process data through Bronze (raw JSON), Silver (flattened/cleaned), and Gold (analytical schemas) layers using S3 and Athena.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Libraries:** `requests`, `pandas`, `boto3` (AWS SDK), `logging`
* **Target Infrastructure (AWS):** S3 (Data Lake), Lambda (Compute), Athena (SQL Engine), EventBridge (Orchestration)

## 🔜 Next Steps / Roadmap
- [x] **Phase 1: Robust API Ingestion** - Define architecture and implement a resilient API client with pagination and exponential backoff.
- [ ] **Phase 2: Infrastructure as Code (IaC)** - Define and provision the AWS Serverless architecture (S3, Lambda, EventBridge) using Terraform.
- [ ] **Phase 3: Hybrid Data Ingestion** - Complement API data with targeted Web Scraping to extract user Q&A and written reviews.
- [ ] **Phase 4: Machine Learning & NLP Integration** - Train time-series models for price volatility forecasting and deploy NLP models for sentiment analysis on unstructured text.

---
*Created as a professional portfolio project demonstrating modern Data Engineering and API consumption practices.*