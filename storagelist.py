from azure.storage.blob import BlobServiceClient

# Define your storage account connection string
connection_string = "BlobEndpoint=https://newstorageacnt3321432.blob.core.windows.net/;QueueEndpoint=https://newstorageacnt3321432.queue.core.windows.net/;FileEndpoint=https://newstorageacnt3321432.file.core.windows.net/;TableEndpoint=https://newstorageacnt3321432.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiyx&se=2024-02-16T15:02:42Z&st=2024-02-16T07:02:42Z&spr=https&sig=2oKFXniEkEEvd%2Bz3IrNckGK5ehEO%2F9gAcSnQv4vc7AM%3D"

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# List containers in the storage account
containers = blob_service_client.list_containers()

# Print names of all containers in the storage account
print("Containers:")
for container in containers:
    print(container.name)
    # Get a specific container client
    container_client = blob_service_client.get_container_client(container.name)
    
    # List blobs in the container
    print("Blobs in container:")
    blobs = container_client.list_blobs()
    for blob in blobs:
        print("\t", blob.name)
