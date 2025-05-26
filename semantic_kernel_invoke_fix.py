import asyncio
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Assuming KernelArguments and kernel are defined elsewhere,
# for the purpose of this script, we'll use placeholders.
class KernelArguments:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    def __str__(self):
        return str(self.kwargs)

class MockFunction:
    def __init__(self, name):
        self.name = name
    async def __call__(self, *args, **kwargs):
        # Simulate a result that might be a dict or a string
        # return {"sub_category": "misc"} 
        return "Some string result with sub_category: refresh"

class MockSkill:
    def __init__(self):
        self.skill = {"ClassifyIntent": MockFunction("ClassifyIntent")}
    def __getitem__(self, key):
        return self.skill[key]

class MockKernel:
    def add_plugin(self, parent_directory, plugin_name):
        print(f"MockKernel: Adding plugin {plugin_name} from {parent_directory}")
        return MockSkill()
    async def invoke(self, func, arguments):
        print(f"MockKernel: Invoking {func.name} with {arguments}")
        # Simulate a result
        # return {"sub_category": "misc"}
        # return "Some string result with sub_category: refresh"
        # return "No subcategory here"
        return {"plugin_name": "IntentClassificationSkill", "function_name": "ClassifyIntent", "sub_category": "misc"}


kernel = MockKernel() # Placeholder for actual kernel

async def main():
    # ... (initial setup code) ...

    # Set the user question
    q = "List of Devices to be refreshed?"
    plugin_path = "C:/Users/deepasaw/OneDrive - Microsoft/Desktop/LanguagetoSQL/MSD"
    categoryandsubcategoryidentification = None 
    # subcategory = None # Initialize subcategory here -- will be initialized later

    try:
        IntentClassificationSkill = kernel.add_plugin(
            parent_directory=plugin_path,
            plugin_name="IntentClassificationSkill"
        )
        categoryandsubcategoryidentification = IntentClassificationSkill["ClassifyIntent"]
        print(f"Plugin 'IntentClassificationSkill' and function 'ClassifyIntent' loaded successfully.")
    except Exception as e:
        print(f"Error adding plugin or getting function: {e}")
        print(f"Please ensure 'plugin_path' ('{plugin_path}') is correct and the plugin 'IntentClassificationSkill' with function 'ClassifyIntent' exists.")

    arguments = KernelArguments(question=q)

    if categoryandsubcategoryidentification:
        try:
            print(f"Invoking {categoryandsubcategoryidentification.name} with arguments: {arguments}...")
            result = await kernel.invoke(categoryandsubcategoryidentification, arguments)
            print("Invocation result:")
            print(result)
        except Exception as e:
            print(f"Error during function invocation: {e}")
            result = f"Error: {e}"
    else:
        print("Skipping function invocation because 'categoryandsubcategoryidentification' is None (plugin might have failed to load).")
        result = "Function not invoked due to plugin load failure."

    print(f"Script semantic_kernel_invoke_fix.py main() executed. Q: {q}")

    # --- Embedding-based semantic search and prompt generation (Open Source) ---
    # Load CSV with questions and SQL queries
    # Using a dummy CSV content for local execution
    from io import StringIO
    csv_data = """question,sql_query
"What are the devices to be refreshed?","SELECT DeviceName FROM Devices WHERE Status = 'Refresh'"
"List all servers.","SELECT ServerName FROM Servers"
"Show active users.","SELECT UserName FROM Users WHERE IsActive = TRUE"
"Which devices have low disk space?","SELECT DeviceID, DiskSpace FROM Devices WHERE DiskSpace < 10"
"""
    csv_path = StringIO(csv_data) # Use StringIO for dummy data
    # csv_path = r"C:\Users\deepasaw\OneDrive - Microsoft\Desktop\LanguagetoSQL\MSD\Plugins\devicerefresh.csv" # Corrected path for Windows
    df = pd.read_csv(csv_path)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    df["embedding"] = df["question"].apply(lambda x: model.encode(x, convert_to_numpy=True))
    question_embedding = model.encode(q, convert_to_numpy=True)
    df["similarity"] = df["embedding"].apply(lambda emb: cosine_similarity([emb], [question_embedding])[0][0])
    top2 = df.nlargest(2, "similarity")
    result_str = ""
    for idx, row in top2.iterrows():
        result_str += f'For Question : {row["question"]},\n"SQLQuery to be returned or the Output should be": {row["sql_query"]}\n'

    base_prompt = "This is the base prompt."
    refresh_table_creation = "This is the refresh table creation instruction."

    # Initialize subcategory to None before the if/elif/else block
    subcategory = None 
    
    # This is the section to be modified
    if isinstance(result, dict):
        subcategory = result.get('sub_category')
    elif hasattr(result, 'get'): # For objects that behave like dicts but aren't dicts
        subcategory = result.get('sub_category', None)
    elif isinstance(result, str):
        # import re # Moved to top
        m = re.search(r"sub[_ ]?category['"]?\s*[:=]\s*['"]?([\w ]+)", result, re.IGNORECASE)
        if m:
            subcategory = m.group(1).strip() # Added strip()
        # else: subcategory remains None if regex doesn't match

    # --- Corrected final_prompt construction ---
    final_prompt = base_prompt 
    if subcategory is not None and (str(subcategory).lower() == 'misc' or 'refresh' in str(subcategory).lower()):
        final_prompt += "\n" + refresh_table_creation
    
    # Always append result_str after potentially adding refresh_table_creation
    final_prompt += "\n" + result_str 
    print("--- Final Prompt ---")
    print(final_prompt)

if __name__ == "__main__":
    asyncio.run(main())
