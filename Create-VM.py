# import logging
# from azure.identity import AzureCliCredential
# from azure.mgmt.compute import ComputeManagementClient
# from azure.mgmt.network import NetworkManagementClient
# from azure.mgmt.resource import ResourceManagementClient
# import os
 
# print("Provisioning VMs in Azure")
 
# credential = AzureCliCredential()
 
# sub_id = os.environ["Azure_Sub_Id"] = "71815b3c-ac05-4504-8f3f-6d7f27ce722f"
 
# rg_client = ResourceManagementClient(credential, sub_id)
 
# RESOURCE_GROUP_NAME = "RG-Python-VM"
 
# LOCATION = "westus"
 
# result = rg_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME, {"location": LOCATION})
 
# print(f"Provisioning the resource group {result.name} to the region {result.location}")
 
# VNET_NAME = "vnet-example"
# SUBNET_NAME = "subnet-example"
# IP_CONFIG_NAME = "ip-config-example"
# NIC_NAME_PREFIX = "nic-example"
# VM_NAME_PREFIX = "vm-example"
# USER_NAME = input("Enter Username:")
# PASSWORD = input("Enter Password:")
 
# network_client = NetworkManagementClient(credential, sub_id)
 
# for i in range(3):
#     NIC_NAME = f"{NIC_NAME_PREFIX}-{i}"
#     VM_NAME = f"{VM_NAME_PREFIX}-{i}"
#     IP_NAME = f"ip-example-{i}"  # Unique IP name for each NIC
 
#     print(f"Provisioning VM {VM_NAME}; this operation may take a few minutes!")
 
#     # Create virtual network and subnet if not already created
#     if i == 0:
#         poller = network_client.virtual_networks.begin_create_or_update(
#             RESOURCE_GROUP_NAME,
#             VNET_NAME,
#             {
#                 "location": LOCATION,
#                 "properties": {
#                     "addressSpace": {
#                         "addressPrefixes": ["10.0.0.0/16"]
#                     }
#                 }
#             }
#         )
#         vnet_result = poller.result()
 
#         poller = network_client.subnets.begin_create_or_update(
#             RESOURCE_GROUP_NAME,
#             VNET_NAME,
#             SUBNET_NAME,
#             {"addressPrefix": "10.0.0.0/24"}
#         )
#         subnet_result = poller.result()
 
#     # Create a new public IP address for each NIC
#     poller = network_client.public_ip_addresses.begin_create_or_update(
#         RESOURCE_GROUP_NAME, IP_NAME, {
#             "location": LOCATION,
#             "public_ip_allocation_method": "Static",
#             "public_ip_address_version": "IPv4"
#         })
 
#     ip_address_result = poller.result()
 
#     poller = network_client.network_interfaces.begin_create_or_update(
#         RESOURCE_GROUP_NAME,
#         NIC_NAME,
#         {
#             "location": LOCATION,
#             "ip_configurations": [{
#                 "name": IP_CONFIG_NAME,
#                 "subnet": {"id": subnet_result.id},
#                 "public_ip_address": {"id": ip_address_result.id}
#             }]
#         })
 
#     nic_result = poller.result()
 
#     Compute_client = ComputeManagementClient(credential, sub_id)
 
#     poller = Compute_client.virtual_machines.begin_create_or_update(
#         RESOURCE_GROUP_NAME, VM_NAME,
#         {
#             "location": LOCATION,
#             "storage_profile": {
#                 "image_reference": {
#                     "publisher": 'MicrosoftWindowsServer',
#                     "offer": "WindowsServer",
#                     "sku": "2019-datacenter",
#                     "version": "latest"
#                 }
#             },
#             "hardware_profile": {
#                 "vm_size": "Standard_DS2_v2"
#             },
#             "os_profile": {
#                 "computer_name": VM_NAME,
#                 "admin_username": USER_NAME,
#                 "admin_password": PASSWORD
#             },
#             "network_profile": {
#                 "network_interfaces": [{
#                     "id": nic_result.id,
#                 }]
#             }
#         })
 
#     vm_result = poller.result()
 
#     print(f"Provisioning virtual machine {vm_result.name}")
 
# print("All virtual machines provisioned successfully!")