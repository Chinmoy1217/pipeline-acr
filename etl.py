import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
import requests
from io import StringIO

# Environment Variables
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
logic_app_url = os.getenv("LOGIC_APP_URL")
container_name = "manifest"
source_prefix = "inbound/"
destination_prefix = "outbound/"

# Notify Logic App
def send_status(status, message):
    try:
        if logic_app_url:
            requests.post(logic_app_url, json={"status": status, "message": message})
    except Exception as e:
        print(f"Failed to notify Logic App: {e}")

# Initialize processed files counter
processed_files = 0

try:
    # Connect to Azure Blob Storage
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client(container_name)

    # List blobs in inbound/
    blob_list = container_client.list_blobs(name_starts_with=source_prefix)

    for blob in blob_list:
        if blob.name.endswith(".csv"):
            processed_files += 1
            print(f"Processing {blob.name}")
            
            # Download CSV data
            blob_client = blob_service.get_blob_client(container_name, blob.name)
            data = blob_client.download_blob().readall().decode('utf-8')

            # Read into DataFrame and keep only first 1000 rows
            df = pd.read_csv(StringIO(data))
            df = df.head(1000)

            # Convert back to CSV
            output = df.to_csv(index=False)

            # Upload to outbound/ folder with same filename
            filename = blob.name.split("/")[-1]
            dest_blob_path = f"{destination_prefix}{filename}"
            dest_blob_client = blob_service.get_blob_client(container_name, dest_blob_path)
            dest_blob_client.upload_blob(output, overwrite=True)

    # Determine success message based on files processed
    if processed_files == 0:
        send_status("Success", "ETL completed - no files to process")
    else:
        send_status("Success", f"ETL completed successfully - processed {processed_files} files")

except Exception as e:
    # Notify Logic App of failure with processed files count
    send_status("Failure", f"ETL pipeline failed after processing {processed_files} files: {str(e)}")
    raise