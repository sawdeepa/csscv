from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import os

# --- Download Logic (reused for robustness) ---
repo_id_download = "Elixpo/LlamaMedicine"
filename_download = "unsloth.Q8_0.gguf"
download_dir = "./temp"
gguf_model_path = os.path.join(download_dir, "LlamaMedicine_unsloth.Q8_0.gguf")

os.makedirs(download_dir, exist_ok=True)

if not os.path.exists(gguf_model_path):
    print(f"Model file not found at {gguf_model_path}. Attempting to download...")
    try:
        print(f"Starting download of {filename_download} from {repo_id_download} to {download_dir}...")
        downloaded_path_from_hub = hf_hub_download(
            repo_id=repo_id_download,
            filename=filename_download,
            local_dir=download_dir,
            local_dir_use_symlinks=False,
        )
        expected_hub_filename_in_dir = os.path.join(download_dir, filename_download)
        if os.path.abspath(expected_hub_filename_in_dir) != os.path.abspath(gguf_model_path):
            print(f"File downloaded to {expected_hub_filename_in_dir}. Renaming to {gguf_model_path}.")
            os.rename(expected_hub_filename_in_dir, gguf_model_path)
        else:
            print(f"File downloaded as {expected_hub_filename_in_dir}.")

        if not os.path.exists(gguf_model_path):
            print(f"Error: File still not found at {gguf_model_path} after download and rename attempt.")
            exit()
        print(f"Successfully downloaded model to {gguf_model_path}")
    except Exception as e:
        print(f"An error occurred during model download: {e}")
        import traceback
        traceback.print_exc()
        exit()
else:
    print(f"Model file already exists at {gguf_model_path}. Skipping download.")

# --- Load Model and Generate Response ---
print(f"Attempting to load GGUF model from: {gguf_model_path}")
llm = None # Initialize llm to None
try:
    llm = Llama(model_path=gguf_model_path, verbose=True)
    print("GGUF model loaded successfully.")

    prompt = "Question: what should i eat if I have calcium deficiency? Answer:"
    print(f"\nPrompt: {prompt}")

    # Generate completion
    # Note: create_completion is more aligned with older OpenAI API style.
    # For newer llama-cpp-python versions, using llm(prompt, ...) is also common for direct completions.
    output = llm.create_completion(
        prompt,
        max_tokens=512,  # Max tokens to generate
        stop=["Question:", "\n\n"],  # Stop generating if it encounters these sequences
        temperature=0.7, # Add some temperature for variability, adjust as needed
        # top_p=0.9,       # Example: nucleus sampling
        # top_k=40,        # Example: top-k sampling
        # repeat_penalty=1.1 # Example: penalize repetition
    )

    generated_text = output['choices'][0]['text']
    print("\nGenerated Answer:")
    print(generated_text)

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Explicitly free the model from memory if it was loaded
    if llm is not None:
        # The __del__ method in Llama should handle this, but explicit can be good in scripts
        # Depending on the version of llama-cpp-python, there might not be an explicit del or free method.
        # We'll rely on Python's garbage collection here for simplicity as Llama object goes out of scope.
        print("\nModel resources will be released when script ends.")


print("\nScript finished.")
