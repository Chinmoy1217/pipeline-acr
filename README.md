# ETL Pipeline with Azure Blob Storage, Docker & Logic App Notification

This project reads CSV files from an Azure Blob Storage container, removes the last column if more than 5 columns exist, and writes them to another container. Status notifications (success/failure) are sent to a Logic App via HTTP.

## ✅ Features
- Reads CSVs from `inbound` container
- Removes 1 column if column count > 5
- Uploads cleaned files to `outbound` container
- Sends success/failure status to Azure Logic App

## 🐳 Docker Usage

### Build and Run Locally
```bash
docker build -t etl-csv .
docker run --env-file .env etl-csv