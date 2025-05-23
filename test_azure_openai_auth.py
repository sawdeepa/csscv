# This script tests Azure OpenAI authentication using DefaultAzureCredential.
# It attempts to fetch an Azure AD token and use it to make a simple API call
# to the chat completions endpoint.
#
# How to interpret the output:
# - Successful token fetching: Indicates that DefaultAzureCredential was able to obtain a token.
#   This means one of its authentication methods (e.g., environment variables, Managed Identity, Azure CLI) worked.
# - Successful API call (e.g., Status Code 200): Shows that the fetched token is valid for accessing
#   the specified Azure OpenAI resource and deployment. The response JSON will be printed.
# - Potential errors:
#   - Token fetching errors: Often indicate issues with the Azure AD setup, permissions,
#     or the environment where the script is run (e.g., missing Managed Identity, not logged into Azure CLI).
#   - API request errors (e.g., 401, 403, 404):
#     - 401 (Unauthorized): The token might be invalid, expired, or not for the correct audience.
#     - 403 (Forbidden): The identity associated with the token does not have permission
#       (e.g., the "Cognitive Services OpenAI User" role) on the Azure OpenAI resource.
#     - 404 (Not Found): The Azure OpenAI endpoint or deployment name might be incorrect.
#   - HTTPX errors: Indicate network issues or problems reaching the endpoint.

import os
import asyncio
from azure.identity import DefaultAzureCredential
import httpx # For making asynchronous HTTP requests

# Defines the main asynchronous function for the script.
async def main():
    # --- Environment Variable Setup ---
    # Retrieve required environment variables.
    # AZURE_OPENAI_ENDPOINT: The base URL of your Azure OpenAI resource (e.g., https://your-resource.openai.azure.com).
    # AZURE_OPENAI_DEPLOYMENT_NAME: The name of your chat model deployment (e.g., gpt-35-turbo).
    print("Loading environment variables...")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # Check if environment variables are set, providing guidance if not.
    if not azure_openai_endpoint or not azure_openai_deployment_name:
        missing_vars = []
        if not azure_openai_endpoint:
            missing_vars.append("AZURE_OPENAI_ENDPOINT")
        if not azure_openai_deployment_name:
            missing_vars.append("AZURE_OPENAI_DEPLOYMENT_NAME")
        print(f"Error: The following environment variables are not set: {', '.join(missing_vars)}. Please set them and try again.")
        print("  AZURE_OPENAI_ENDPOINT should be like: https://your-openai-resource.openai.azure.com")
        print("  AZURE_OPENAI_DEPLOYMENT_NAME is the name of your deployment, e.g., 'gpt-4o'")
        return

    print(f"  AZURE_OPENAI_ENDPOINT: {azure_openai_endpoint}")
    print(f"  AZURE_OPENAI_DEPLOYMENT_NAME: {azure_openai_deployment_name}")

    # --- Token Fetching using DefaultAzureCredential ---
    # DefaultAzureCredential attempts authentication through a chain of methods:
    # 1. Environment variables (e.g., for service principals).
    # 2. Managed Identity (if running on an Azure host with MI enabled).
    # 3. Azure CLI (if logged in via `az login`).
    # Other methods like Azure Developer CLI, Azure PowerShell, and InteractiveBrowserCredential are also supported.
    print("\nInstantiating DefaultAzureCredential...")
    credential = DefaultAzureCredential()

    # Fetch an access token for Azure Cognitive Services.
    # The scope "https://cognitiveservices.azure.com/.default" is standard for Azure OpenAI resources.
    print("Attempting to fetch token using DefaultAzureCredential for scope 'https://cognitiveservices.azure.com/.default'...")
    try:
        token_object = await credential.get_token("https://cognitiveservices.azure.com/.default")
        print("Token fetched successfully.")
        # For security, avoid printing the token itself in production logs.
        # print(f"Token (first 10 chars): {token_object.token[:10]}...")
    except Exception as e:
        print(f"Error fetching token: {e}")
        print("  Common causes for token errors:")
        print("  - Script not running in an environment where DefaultAzureCredential can find credentials (e.g., Azure VM with Managed Identity, local dev with Azure CLI login).")
        print("  - The identity (user, service principal, or Managed Identity) lacks permissions to access Azure services or to obtain tokens.")
        print("  - Incorrect Azure AD tenant configuration or conditional access policies.")
        return

    # --- API Call Preparation ---
    # Construct the API URL for the chat completions endpoint.
    # Ensure the endpoint does not have a trailing slash for correct URL construction.
    # The api-version can be updated as needed for newer Azure OpenAI API versions.
    api_url = f"{azure_openai_endpoint.rstrip('/')}/openai/deployments/{azure_openai_deployment_name}/chat/completions?api-version=2023-05-15"
    
    # Define a simple payload for the chat completions request.
    payload = {
        "messages": [{"role": "user", "content": "This is a test to check authentication."}],
        "max_tokens": 5 # Keep max_tokens low for a simple test.
    }
    # Set up headers, including the Authorization Bearer token.
    headers = {
        "Authorization": f"Bearer {token_object.token}",
        "Content-Type": "application/json"
    }

    # --- Making the HTTP Request ---
    print(f"\nAttempting to call Azure OpenAI API at: {api_url}")
    # Make an asynchronous POST request to the Azure OpenAI API.
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, headers=headers, timeout=30.0)
            
            print(f"API Response Status Code: {response.status_code}")
            try:
                response_json = response.json()
                print(f"API Response JSON: {response_json}")
            except Exception as json_err: # Catch potential JSON decoding errors
                print(f"Could not decode API Response JSON: {json_err}")
                print(f"API Response Text: {response.text}")


            if response.is_success:
                print("\nAPI request successful. Authentication and basic API call seem to be working.")
                print("  A status code of 200 OK with a valid JSON response containing 'choices' indicates success.")
            else:
                print(f"\nAPI request failed. Status: {response.status_code}")
                print("  Common causes for API call failures (after successful token fetch):")
                print("  - 401 Unauthorized: Token might be for the wrong audience or has insufficient claims. Double-check token scope and permissions.")
                print("  - 403 Forbidden: The identity used to fetch the token does not have the required data plane role (e.g., 'Cognitive Services OpenAI User') on the Azure OpenAI resource.")
                print("  - 404 Not Found: The endpoint or deployment name in AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_DEPLOYMENT_NAME might be incorrect.")
                print("  - Other status codes might indicate issues with the request payload, API version, or Azure OpenAI service itself.")
                
    except httpx.RequestError as req_err:
        print(f"HTTPX RequestError during API call: {req_err}")
        print("  This usually indicates a network issue, DNS problem, or that the Azure OpenAI endpoint is unreachable.")
    except Exception as e:
        print(f"An unexpected error occurred during the API call: {e}")

# Standard Python entry point for asynchronous scripts.
if __name__ == "__main__":
    asyncio.run(main())
