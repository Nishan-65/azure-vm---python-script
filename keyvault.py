from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceExistsError
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import VaultProperties, Sku, AccessPolicyEntry, Permissions, \
    KeyPermissions, SecretPermissions, CertificatePermissions

# Replace these values with your Azure subscription and resource group information
tenant_id = "fb9c6107-5a03-4ff4-8b38-9ea249a7077d"
subscription_id = '71815b3c-ac05-4504-8f3f-6d7f27ce722f'
resource_group_name = 'key-vault'
vault_name = 'kevaultnew3445'

# Initialize the default Azure credential
credential = DefaultAzureCredential()

# Create a Resource Management Client
resource_client = ResourceManagementClient(credential, subscription_id)

# Define the location where the resource group will be created
location = "eastus"  # Replace with your desired Azure region

# Create Resource Group
try:
    resource_group_params = ResourceGroup(location=location)
    resource_group = resource_client.resource_groups.create_or_update(resource_group_name, resource_group_params)
    print(f"Resource group '{resource_group_name}' created successfully.")
except ResourceExistsError:
    print(f"Resource group '{resource_group_name}' already exists.")
except Exception as e:
    print(f"An error occurred while creating the resource group: {e}")

# Create Key Vault Management Client
keyvault_client = KeyVaultManagementClient(credential, subscription_id)

# Define access policies
access_policies = [
    AccessPolicyEntry(
        tenant_id=tenant_id,  # Use the provided tenant ID directly
        object_id="5c468b47-0ae6-49a8-aa7b-93051458e4e1",  # Replace with the Object ID of the user/service principal
        permissions=Permissions(
            keys=[KeyPermissions.get, KeyPermissions.create, KeyPermissions.delete, KeyPermissions.list],
            secrets=[SecretPermissions.get, SecretPermissions.list]
        )
    )
]

# Define SKU
sku = Sku(name='standard', family='A')

# Create Key Vault
try:
    vault_properties = VaultProperties(
        tenant_id=tenant_id,  # Use the provided tenant ID directly
        sku=sku,
        access_policies=access_policies
    )
    poller = keyvault_client.vaults.begin_create_or_update(
        resource_group_name,
        vault_name,
        {
            'location': location,
            'properties': vault_properties
        }
    )
    vault = poller.result()
    print(f"Key Vault '{vault_name}' created successfully.")
except ResourceExistsError:
    print(f"Key Vault '{vault_name}' already exists.")
except Exception as e:
    print(f"An error occurred while creating the Key Vault: {e}")
