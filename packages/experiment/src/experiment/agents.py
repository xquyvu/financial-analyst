import os

from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

from shared.config import ASYNC_CREDENTIAL, SYNC_CREDENTIAL

load_dotenv()


def get_agent_client() -> AzureAIAgentClient:
    return AzureAIAgentClient(
        async_credential=ASYNC_CREDENTIAL,
        model_deployment_name="gpt-4.1-mini",
    )


def get_project_client() -> AIProjectClient:
    return AIProjectClient(
        credential=SYNC_CREDENTIAL,
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    )
