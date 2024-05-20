from google.cloud import storage
import os
import pandas as pd

# set key credentials file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"./IAM_admin.json"


# define function that creates the bucket
def create_bucket(bucket_name, storage_class="STANDARD", location="us-central1"):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = storage_class

    bucket = storage_client.create_bucket(bucket, location=location)
    # for dual-location buckets add data_locations=[region_1, region_2]

    return f"Bucket {bucket.name} successfully created."


# define function that downloads a file from the bucket
def download_cs_file(bucket_name, file_name, destination_file_name):
    storage_client = storage.Client()
    print("client conn")
    bucket = storage_client.bucket(bucket_name)
    print("bucket")
    blob = bucket.blob(file_name)
    blob.download_to_filename(destination_file_name)
    print("complete")
    return True


df = pd.read_csv("resumes.csv")
# os.mkdir("resumes")

for i, v in df.iterrows():
    try:
        url = v["url"].replace("%40", "@")
        key = url.split("/")[-1]
        print(key)
        download_cs_file("mercor_dashboard_data", key, f"./resumes/{key}")
    except Exception as e:
        print(
            f"Error: {e}: ",
            key,
        )
