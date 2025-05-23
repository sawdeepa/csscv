import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import os,openai
import pyodbc
import pandas as pd
from azure.identity import ClientSecretCredential # Unused in this flow
from azure.identity import InteractiveBrowserCredential

# Set up environment variables
db_host = os.getenv("server_name")
db_name = os.getenv("database_name")
driver = "ODBC+Driver+17+for+SQL+Server" # Unused in this flow
client_id = os.getenv("client_id") # Unused in this flow
client_secret = os.getenv("AZURE_CLIENT_SECRET") # Unused in this flow
tenant_id = os.getenv("tenant_id")
endpoint =  os.getenv("endpoint")
deployment =  os.getenv("deployment")


# Authenticate using your user identity (interactive browser)
# InteractiveBrowserCredential is used to obtain an Azure AD token.
credential = InteractiveBrowserCredential(tenant_id=tenant_id)

print("Attempting to fetch token via Interactive Browser... This may open a browser window.") # User guidance
try:
    # The get_token method is called with the standard Azure Cognitive Services scope.
    # This action will trigger a browser-based login flow.
    access_token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    print("Successfully fetched access token.")
except Exception as e:
    print(f"Error fetching token: {e}")
    access_token = None # Ensure access_token is defined even on error
    # Optionally, re-raise the exception or handle it more gracefully depending on desired script behavior

# Initialize Semantic Kernel
kernel = sk.Kernel()

# Add AzureChatCompletion as a service if access_token was fetched
if access_token:
    print("Adding AzureChatCompletion service with fetched token.")
    # The fetched access_token is passed to AzureChatCompletion via the api_key parameter.
    # ad_auth=True is also passed, signaling that the api_key should be treated as an Azure AD token.
    # This approach is used because the direct `credential=` keyword argument was not supported
    # by the version of AzureChatCompletion being used (as indicated by a previous TypeError).
    chat_service = AzureChatCompletion(
        deployment_name=deployment,
        endpoint=endpoint,
        api_key=access_token,  # Pass the fetched token as api_key
        ad_auth=True          # Flag to indicate Azure AD authentication (token-based)
    )
    kernel.add_service("chat_completion", chat_service)
    # Note: Subsequent code that uses this service (e.g., creating context, calling complete)
    # should ideally also be within this block or handle the case where the service is not added.
    # For this task, we are focusing on the AzureChatCompletion initialization.
else:
    print("AzureChatCompletion service not added due to token fetching failure.")

# ... rest of the script
# Example of how the service might be used (from original user script structure):
# context = kernel.create_new_context()
# context["question"] = "How are you?"
# if kernel.has_service("chat_completion"): # Good practice to check
#     chat = kernel.get_service("chat_completion")
#     response = chat.complete(prompt=context["question"])
#     print(response)
# else:
#     print("Chat service not available.")

print("Script setup complete for semantic_kernel_interactive_auth.py.")
