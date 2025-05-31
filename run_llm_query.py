#!/usr/bin/env python3
import os
import sys
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1. Define constants
MODEL_REPO_ID = "Elixpo/LlamaMedicine"
MODEL_FILENAME = "unsloth.Q8_0.gguf" # Using the original filename from the repo for download
MODEL_DOWNLOAD_DIR = "./temp_model_data"
# For consistency, let's save the model with its original filename in the download dir
MODEL_FILE_PATH = os.path.join(MODEL_DOWNLOAD_DIR, MODEL_FILENAME)

PROMPT_QUESTION = "what should i eat if I have calcium deficiency?"

# 2. Implement download function
def download_model_if_needed(repo_id, filename_on_hub, download_dir, local_model_path):
    """
    Downloads the model from Hugging Face Hub if it's not already present locally.
    Manages renaming if the downloaded filename needs to be adjusted to local_model_path.
    """
    os.makedirs(download_dir, exist_ok=True)

    if not os.path.exists(local_model_path):
        print(f"Model not found at {local_model_path}. Downloading...", file=sys.stderr)
        try:
            # Download the file using its name on the hub
            downloaded_path_from_hub = hf_hub_download(
                repo_id=repo_id,
                filename=filename_on_hub, # This is MODEL_FILENAME
                local_dir=download_dir,
                local_dir_use_symlinks=False, # Download actual file
            )

            # After download, downloaded_path_from_hub will be download_dir/filename_on_hub
            # If local_model_path is different (e.g., we want a different local name), rename.
            # In this script setup, filename_on_hub IS the name part of local_model_path.
            # So, downloaded_path_from_hub should be identical to local_model_path.
            # Adding a check and rename just in case for robustness or future changes.
            if os.path.abspath(downloaded_path_from_hub) != os.path.abspath(local_model_path):
                print(f"File downloaded to {downloaded_path_from_hub}. Moving to {local_model_path}.", file=sys.stderr)
                # Ensure no old file at target path if it's different from where hf_hub downloaded
                if os.path.exists(local_model_path):
                    os.remove(local_model_path)
                os.rename(downloaded_path_from_hub, local_model_path)

            if os.path.exists(local_model_path):
                 print(f"Model successfully downloaded to {local_model_path}", file=sys.stderr)
            else:
                raise FileNotFoundError(f"Model download failed, file not found at {local_model_path} or {downloaded_path_from_hub}")

        except Exception as e:
            print(f"Error during model download: {e}", file=sys.stderr)
            raise
    else:
        print(f"Model found at {local_model_path}. Skipping download.", file=sys.stderr)

# 3. Implement response generation function
def generate_response(model_path, prompt_text):
    """
    Loads the GGUF model and generates a response to the given prompt.
    """
    print(f"Loading model from {model_path}...", file=sys.stderr)
    llm = None
    try:
        llm = Llama(model_path=model_path, verbose=False)
        print("Model loaded successfully.", file=sys.stderr)

        formatted_prompt = f"Question: {prompt_text} Answer:"
        print(f"Generating response for prompt: \"{formatted_prompt}\"", file=sys.stderr)

        output = llm.create_completion(
            formatted_prompt,
            max_tokens=512,
            stop=["Question:", "\n\n", "\nQuestion"], # Added more stop tokens
            temperature=0.7
        )

        response_text = output['choices'][0]['text'].strip()
        return response_text
    except Exception as e:
        print(f"Error during response generation: {e}", file=sys.stderr)
        raise
    finally:
        if llm is not None:
            # llama-cpp-python models are freed when the Llama object is garbage collected.
            # No explicit llm.free() or del llm is strictly necessary here.
            print("Model resources will be freed upon script completion.", file=sys.stderr)


# 4. Main execution block
if __name__ == "__main__":
    try:
        download_model_if_needed(
            repo_id=MODEL_REPO_ID,
            filename_on_hub=MODEL_FILENAME, # Use the actual filename from the hub
            download_dir=MODEL_DOWNLOAD_DIR,
            local_model_path=MODEL_FILE_PATH
        )

        response = generate_response(MODEL_FILE_PATH, PROMPT_QUESTION)

        print("\n--- Generated Response ---")
        print(response)
        print("--- End of Response ---")

    except FileNotFoundError as e:
        print(f"Critical error: Model file not found. {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected critical error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
