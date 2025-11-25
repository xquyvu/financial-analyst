from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

SYNC_CREDENTIAL = DefaultAzureCredential()
ASYNC_CREDENTIAL = AsyncDefaultAzureCredential()
