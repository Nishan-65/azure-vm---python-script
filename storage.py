from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, Kind
from azure.core.exceptions import HttpResponseError

# Replace these variables with your desired values
subscription_id = '71815b3c-ac05-4504-8f3f-6d7f27ce722f'
resource_group_name = 'storageacnt'
storage_account_name = 'newstorageacnt3321432'
location = 'eastus2'
container_name = 'container-01'
local_file_path = 'C:/Users/DELL7480/Desktop/download.jpg'
blob_name = 'download'

# Initialize the StorageManagementClient
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, subscription_id)

# Create the resource group
resource_group_params = {'location': location}
resource_group = resource_client.resource_groups.create_or_update(resource_group_name, ResourceGroup(**resource_group_params))
print(f"Resource group '{resource_group_name}' created successfully.")

# Initialize the StorageManagementClient
storage_client = StorageManagementClient(credential, subscription_id)

# Create parameters for the storage account
sku = Sku(name='Standard_RAGRS')  # You can change the SKU as needed
kind = Kind.storage  # Change to Kind.storagev2 for V2 accounts
parameters = StorageAccountCreateParameters(
    sku=sku,
    kind=kind,
    location=location
)

# Create the storage account
try:
    storage_account = storage_client.storage_accounts.begin_create(
        resource_group_name,
        storage_account_name,
        parameters
    ).result()
    print(f"Storage account '{storage_account_name}' created successfully.")

    # Get the connection string for the newly created storage account
    storage_key = storage_client.storage_accounts.list_keys(resource_group_name, storage_account_name)
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_key.keys[0].value};EndpointSuffix=core.windows.net"

    # Create a BlobServiceClient using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a new container
    container_client = blob_service_client.get_container_client(container_name)
    container_client.create_container()

    print(f"Container '{container_name}' created successfully.")

    # Upload a file to the container
    with open(local_file_path, "rb") as data:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data)

    print(f"File '{blob_name}' uploaded to container '{container_name}' successfully.")

except HttpResponseError as e:
    print(e)
