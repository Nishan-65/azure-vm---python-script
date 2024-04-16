import logging
from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.keyvault.secrets import SecretClient
from azure.mgmt.resource.resources.models import DeploymentMode
import os
import secrets
import string

print("Provisioning a VM in Azure")

credential = AzureCliCredential()

# Define the tenant_id
tenant_id = "fb9c6107-5a03-4ff4-8b38-9ea249a7077d"

sub_id = "71815b3c-ac05-4504-8f3f-6d7f27ce722f"  # Your Azure subscription ID

# Assuming you have the names of the existing Key Vault and resource group
RESOURCE_GROUP_NAME = "TEXIIO-RG-16-4-2024"
KV_NAME = "kevaultnew34459"

# Initialize clients for the existing resources
kv_client = KeyVaultManagementClient(credential, sub_id)
rg_client = ResourceManagementClient(credential, sub_id)
network_client = NetworkManagementClient(credential, sub_id)
compute_client = ComputeManagementClient(credential, sub_id)

# Fetch existing Key Vault
vault = kv_client.vaults.get(RESOURCE_GROUP_NAME, KV_NAME)

location = vault.location

print(f"Using existing Key Vault {vault.name} in the region {location}")

# Storing username and password in Key Vault
USERNAME = input("Enter Username:")
PASSWORD = input("Enter Password:")

# Create a SecretClient
keyvault_url = f"https://{KV_NAME}.vault.azure.net/"
secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

# Set the secrets
keyvault_password_secret_name = "vm-password"
keyvault_username_secret_name = "vm-username"

password_secret = secret_client.set_secret(keyvault_password_secret_name, PASSWORD)
username_secret = secret_client.set_secret(keyvault_username_secret_name, USERNAME)

print(f"Username and password stored in Key Vault: {username_secret.name}, {password_secret.name}")

# Create Virtual Network and Subnet
VNET_NAME = "TEXIIO-VM-KV-VNET"
SUBNET_NAME = "TEXIIO-VM-KV-SUBNET"
ADDRESS_PREFIX = "10.0.0.0/16"
SUBNET_PREFIX = "10.0.2.0/24"

async_vnet_creation = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": location,
        "address_space": {
            "address_prefixes": [ADDRESS_PREFIX]
        }
    }
)
vnet_info = async_vnet_creation.result()

async_subnet_creation = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {"address_prefix": SUBNET_PREFIX}
)
subnet_info = async_subnet_creation.result()

print(f"Virtual Network {VNET_NAME} and Subnet {SUBNET_NAME} created.")

# Create Network Security Group
NSG_NAME = "TEXIIO-VM-KV-NSG"
async_nsg_creation = network_client.network_security_groups.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NSG_NAME,
    {
        "location": location
    }
)
nsg_info = async_nsg_creation.result()

print(f"Network Security Group {NSG_NAME} created.")

# Create Network Interface with NSG
NIC_NAME = "TEXIIO-VM-KV-NIC"
async_nic_creation = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": location,
        "ip_configurations": [{
            "name": "ipconfig1",
            "subnet": {
                "id": subnet_info.id
            }
        }],
        "network_security_group": {
            "id": nsg_info.id
        }
    }
)
nic_info = async_nic_creation.result()

print(f"Network Interface {NIC_NAME} created.")

PUBLIC_IP_NAME = "TEXIIO-VM-KV-PIP"
# Create Public IP Address
async_public_ip_creation = network_client.public_ip_addresses.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    PUBLIC_IP_NAME,
    {
        "location": location,
        "public_ip_allocation_method": "Dynamic"  # You can change this to "Static" if needed
    }
)
public_ip_info = async_public_ip_creation.result()

# VM creation
VM_NAME = input("Enter VM name:")
USER_NAME = input("Enter Username:")

print(f"Provisioning of the VM {VM_NAME}; this operation may take a few minutes!")

poller = compute_client.virtual_machines.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VM_NAME,
    {
        "location": location,
        "storage_profile": {
            "image_reference": {
                "publisher": 'MicrosoftWindowsServer',
                "offer": "WindowsServer",
                "sku": "2019-datacenter",
                "version": "latest"
            }
        },
        "hardware_profile": {
            "vm_size": "Standard_DS2_v2"
        },
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USER_NAME,
            "admin_password": PASSWORD
        },
        "network_profile": {
            "network_interfaces": [{
                "id": nic_info.id,
            }]
        }
    })

vm_result = poller.result()

print(f"Provisioning virtual machine {vm_result.name}")
