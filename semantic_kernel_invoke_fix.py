import semantic_kernel as sk
from semantic_kernel.functions import KernelArguments
# Assuming AzureChatCompletion and DefaultAzureCredential might be used,
# will add them here for completeness based on typical usage context.
# Actual imports will be finalized in a later step.
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from azure.identity import DefaultAzureCredential # For Azure AD based auth
import os
import asyncio # For asynchronous operations with kernel.invoke

# The following imports were noted from user's original broader context.
# They are not directly used in this specific Semantic Kernel invocation part
# but are kept if they were part of the original script structure.
# import openai # If user's script had this, it would be here.
# import pyodbc # If user's script had this, it would be here.
import pandas as pd # Added for DataFrame operations
import openai # Added for the get_embedding function

# --- get_embedding function (Modified for Azure AD Token Auth) ---
# This function is based on the user-provided snippet, modified as per the subtask.
def get_embedding(text, azure_ad_token_str: str, azure_endpoint_url: str, deployment_id="text-embedding-3-large", api_version="2024-02-15"):
    """
    Generates embeddings for the given text using Azure OpenAI service with Azure AD token authentication.

    Args:
        text: The input text to embed.
        azure_ad_token_str: The Azure AD access token string.
        azure_endpoint_url: The Azure OpenAI service endpoint URL.
        deployment_id: The name of the embedding model deployment.
        api_version: The API version for the Azure OpenAI service.

    Returns:
        The embedding vector for the input text, or None if an error occurs.
    """
    # This function authenticates to Azure OpenAI using a passed Azure AD token string (`azure_ad_token_str`)
    # and the specific service endpoint URL (`azure_endpoint_url`).
    # These are used to initialize the openai.AzureOpenAI client for token-based authentication.
    print(f"Attempting to get embedding for text: '{text[:50]}...' using deployment: {deployment_id}")
    try:
        client = openai.AzureOpenAI(
            azure_ad_token=azure_ad_token_str, # Pass the Azure AD token string for authentication.
            api_version=api_version,
            azure_endpoint=azure_endpoint_url  # Specify the Azure OpenAI resource endpoint.
        )
        
        response = client.embeddings.create(input=[text], model=deployment_id)
        embedding = response.data[0].embedding
        print(f"Successfully retrieved embedding. Vector length: {len(embedding)}")
        return embedding
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None

# Defines the main asynchronous function where the primary script logic resides.
# Using `async def` allows the use of `await` for asynchronous operations within this function.
async def main():
    # Placeholder for environment variables and kernel setup
    # This part is assumed to be correctly configured based on previous steps.
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-openai-endpoint.openai.azure.com/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "your-deployment-name")
    # api_key = os.getenv("AZURE_OPENAI_API_KEY") # Not used if DefaultAzureCredential is used

    kernel = sk.Kernel()

    # Example of adding AzureChatCompletion service using DefaultAzureCredential
    # This is illustrative and assumes the user has set it up similarly.
    # Replace this with actual service setup as per your application's needs.
    # For example, if using DefaultAzureCredential:
    try:
        credential = DefaultAzureCredential()
        # Ensure the service_id is unique if multiple services of the same type are added.
        kernel.add_service(
            AzureChatCompletion(
                service_id="chat_completion", # Explicit service_id
                deployment_name=deployment,
                endpoint=endpoint,
                credential=credential
            )
        )
        print("AzureChatCompletion service added using DefaultAzureCredential.")
    except Exception as e:
        print(f"Failed to add AzureChatCompletion service with DefaultAzureCredential: {e}")
        print("Kernel will proceed without this service. Some plugins might not work.")

    # The user's latest version for auth might be token-based (example):
    # try:
    #     interactive_credential = InteractiveBrowserCredential(tenant_id=os.getenv("AZURE_TENANT_ID"))
    #     token_info = interactive_credential.get_token("https://cognitiveservices.azure.com/.default")
    #     kernel.add_service(
    #         AzureChatCompletion(
    #             service_id="chat_completion_token_auth", # Explicit service_id
    #             deployment_name=deployment,
    #             endpoint=endpoint,
    #             api_key=token_info.token, # Pass token as api_key
    #             ad_auth=True # Indicate Azure AD authentication
    #         )
    #     )
    #     print("AzureChatCompletion service added using InteractiveBrowserCredential token.")
    # except Exception as e:
    #     print(f"Failed to add AzureChatCompletion service with InteractiveBrowserCredential token: {e}")
    #     print("Kernel will proceed without this service. Some plugins might not work.")


    # Define q, ensuring it's available
    q = "total number of vulnerable devices?"

    # Add the plugin
    # Ensure the path is correct for your environment or use a relative path.
    # For the sandbox, this path will likely not exist, but we keep it as per user's script.
    # Using the direct path from the user's snippet.
    # It's better to use os.getenv or a configuration for flexibility.
    plugin_path = "C:/Users/deepasaw/OneDrive - Microsoft/Desktop/LanguagetoSQL/MSD"
    # plugin_path = os.getenv("PLUGIN_PATH", "C:/Users/deepasaw/OneDrive - Microsoft/Desktop/LanguagetoSQL/MSD") # Retaining for reference

    categoryandsubcategoryidentification = None # Initialize to None
    try:
        IntentClassificationSkill = kernel.add_plugin(
            parent_directory=plugin_path, # Corrected: user's script uses direct path
            plugin_name="IntentClassificationSkill"
        )
        categoryandsubcategoryidentification = IntentClassificationSkill["ClassifyIntent"]
        print(f"Plugin 'IntentClassificationSkill' and function 'ClassifyIntent' loaded successfully.")
    except Exception as e:
        print(f"Error adding plugin or getting function: {e}")
        print(f"Please ensure 'plugin_path' ('{plugin_path}') is correct and the plugin 'IntentClassificationSkill' with function 'ClassifyIntent' exists.")
        # categoryandsubcategoryidentification remains None

    # Create KernelArguments to pass input to the Semantic Kernel function.
    # 'question=q' maps the variable 'q' to the 'question' input parameter expected by the plugin.
    arguments = KernelArguments(question=q)

    # Invoke the skill function
    if categoryandsubcategoryidentification:
        try:
            print(f"Invoking {categoryandsubcategoryidentification.name} with arguments: {arguments}...")
            # `kernel.invoke` is the standard method to execute a Semantic Kernel function (plugin).
            # `await` is used because `kernel.invoke` is an asynchronous operation.
            # It takes the function object and KernelArguments as input.
            result = await kernel.invoke(categoryandsubcategoryidentification, arguments)
            print("Invocation result:")
            print(result)
        except Exception as e:
            print(f"Error during function invocation: {e}")
            result = f"Error: {e}" # Store error in result for consistent printing if needed
    else:
        print("Skipping function invocation because 'categoryandsubcategoryidentification' is None (plugin might have failed to load).")
        result = "Function not invoked due to plugin load failure." # Placeholder if result is expected later

    print(f"Script semantic_kernel_invoke_fix.py main() executed. Q: {q}")
    # The original script had a simple print(result) at the end.
    # It's now part of the try/except block or the else clause above.

    # --- Placeholder for CSV loading and embedding generation ---
    # This section assumes that 'token', 'azure_openai_endpoint', 'embedding_deployment',
    # 'api_version', 'df', and 'question' are appropriately defined earlier in main().
    # The following calls to `get_embedding` will use the `token.token` (obtained, for example,
    # via DefaultAzureCredential) and `azure_openai_endpoint` for Azure AD authentication.
    
    # Example: Define placeholder variables for the embedding calls
    # These would typically be set up based on your application's needs
    # (e.g., fetching token, loading CSV into a DataFrame, defining the question).
    
    # Placeholder for Azure AD token (assuming it's fetched via DefaultAzureCredential or similar)
    # In a real scenario, this would involve an actual token fetching mechanism.
    class MockToken: # Mocking a token object
        def __init__(self, token_str):
            self.token = token_str
            
    # Attempt to get a real token if DefaultAzureCredential was used for the kernel service
    # This is just for making the example below more functional if a credential was already set up.
    # If not, it will use a dummy token.
    actual_token_str = "DUMMY_TOKEN_FOR_EMBEDDING" # Default dummy token
    if 'credential' in locals() and isinstance(credential, DefaultAzureCredential):
        try:
            print("Attempting to fetch a real token for embedding calls...")
            token_info_for_embedding = await credential.get_token("https://cognitiveservices.azure.com/.default")
            actual_token_str = token_info_for_embedding.token
            print("Successfully fetched real token for embedding.")
        except Exception as e:
            print(f"Could not fetch real token for embedding, using dummy token: {e}")
    
    token = MockToken(actual_token_str) 

    # Use the existing 'endpoint' variable for azure_openai_endpoint if it's suitable,
    # or define specifically if different for embeddings.
    azure_openai_endpoint = endpoint # Assuming the same endpoint is used for embeddings
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large") # Your embedding model deployment
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15") # API version for embeddings

    # Placeholder for DataFrame (e.g., loaded from a CSV)
    # df = pd.read_csv("your_data.csv") # Example: df should have a 'question' column
    data = {'question': ['What is the capital of France?', 'How does photosynthesis work?']}
    df = pd.DataFrame(data)

    # Placeholder for the current question to be embedded
    question_from_sk_invoke = str(result) if 'result' in locals() and result else q # Use SK result or initial q
    question = f"Original question: {q}. Classified intent/result: {question_from_sk_invoke}"


    if not df.empty and 'question' in df.columns:
        print(f"\nUpdating df['embedding'] using get_embedding for {len(df)} rows...")
        df["embedding"] = df["question"].apply(
            lambda x: get_embedding(
                text=x,
                azure_ad_token_str=token.token,
                azure_endpoint_url=azure_openai_endpoint,
                deployment_id=embedding_deployment,
                api_version=api_version
            )
        )
        print("df['embedding'] updated.")
        # print(df.head()) # For debugging
    else:
        print("Skipping df embedding generation as DataFrame is empty or lacks 'question' column.")

    print(f"\nGenerating embedding for the current question: '{question[:100]}...'")
    question_embedding = get_embedding(
        text=question,
        azure_ad_token_str=token.token,
        azure_endpoint_url=azure_openai_endpoint,
        deployment_id=embedding_deployment,
        api_version=api_version
    )
    if question_embedding:
        print("question_embedding generated successfully.")
        # print(f"Question embedding (first 5 values): {question_embedding[:5]}") # For debugging
    else:
        print("Failed to generate question_embedding.")
    # --- End of Placeholder for CSV loading and embedding generation ---


# Standard Python entry point for asynchronous scripts.
# `if __name__ == "__main__":` ensures this code runs only when the script is executed directly.
# `asyncio.run(main())` starts the asyncio event loop and runs the `main()` coroutine.
if __name__ == "__main__":
    asyncio.run(main())
