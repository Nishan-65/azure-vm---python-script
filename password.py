import logging
from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
import os
import secrets
import string

print("Provisioning a VM in Azure")

credential = AzureCliCredential()

sub_id = os.environ["Azure_Sub_Id"] = "71815b3c-ac05-4504-8f3f-6d7f27ce722f"

rg_client = ResourceManagementClient(credential, sub_id)

RESOURCE_GROUP_NAME = "RG-Python-VM"

LOCATION = "westus"

result = rg_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME, {"location": LOCATION})

print(f"Provisioning the resource group {result.name} to the region {result.location}")

VNET_NAME = "vnet-example"
SUBNET_NAME = "subnet-example"
IP_NAME = "ip-example"
IP_CONFIG_NAME = "ip-config-example"
NIC_NAME = "nic-example"

network_client = NetworkManagementClient(credential, sub_id)

poller = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "properties": {
            "addressSpace": {
                "addressPrefixes": ["10.0.0.0/16"]
            }
        }
    }
)

vent_result = poller.result()

poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME,
                                                        VNET_NAME, SUBNET_NAME, {"addressPrefix": "10.0.0.0/24"}
                                                        )

subnet_result = poller.result()

poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME, IP_NAME, {
    "location": LOCATION,
    "public_ip_allocation_method": "Static",
    "public_ip_address_version": "IPv4"
})

ip_address_result = poller.result()

poller = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": LOCATION,
        "ip_configurations": [{
            "name": IP_CONFIG_NAME,
            "subnet": {"id": subnet_result.id},
            "public_ip_address": {"id": ip_address_result.id}
        }]
    }
)

nic_result = poller.result()

Compute_client = ComputeManagementClient(credential, sub_id)

VM_NAME = input("Enter VM name:")
USER_NAME = input("Enter Username:")

# Generating a random password
PASSWORD_LENGTH = 16
PASSWORD = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(PASSWORD_LENGTH))

print(f"Generated random password: {PASSWORD}")

print(f"Provisioning of the VM {VM_NAME}; this operation may take a few minutes!")

poller = Compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
                                                                 {
                                                                     "location": LOCATION,
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
                                                                             "id": nic_result.id,
                                                                         }]
                                                                     }
                                                                 })

vm_result = poller.result()

print(f"Provisioning virtual machine {vm_result.name}")
