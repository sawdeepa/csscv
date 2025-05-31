from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import os
import sys

# --- Download Logic (reused for robustness) ---
repo_id_download = "Elixpo/LlamaMedicine"
filename_download = "unsloth.Q8_0.gguf"
download_dir = "./temp"
gguf_model_path = os.path.join(download_dir, "LlamaMedicine_unsloth.Q8_0.gguf")

os.makedirs(download_dir, exist_ok=True)

if not os.path.exists(gguf_model_path):
    # Keep download messages on stderr to not interfere with stdout capture for the main result
    print(f"Model file not found at {gguf_model_path}. Attempting to download...", file=sys.stderr)
    try:
        print(f"Starting download of {filename_download} from {repo_id_download} to {download_dir}...", file=sys.stderr)
        downloaded_path_from_hub = hf_hub_download(
            repo_id=repo_id_download,
            filename=filename_download,
            local_dir=download_dir,
            local_dir_use_symlinks=False,
        )
        expected_hub_filename_in_dir = os.path.join(download_dir, filename_download)
        if os.path.abspath(expected_hub_filename_in_dir) != os.path.abspath(gguf_model_path):
            print(f"File downloaded to {expected_hub_filename_in_dir}. Renaming to {gguf_model_path}.", file=sys.stderr)
            os.rename(expected_hub_filename_in_dir, gguf_model_path)
        else:
            print(f"File downloaded as {expected_hub_filename_in_dir}.", file=sys.stderr)

        if not os.path.exists(gguf_model_path):
            print(f"Error: File still not found at {gguf_model_path} after download and rename attempt.", file=sys.stderr)
            sys.exit(1) # Exit if download fails
        print(f"Successfully downloaded model to {gguf_model_path}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred during model download: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1) # Exit if download fails
else:
    print(f"Model file already exists at {gguf_model_path}. Skipping download.", file=sys.stderr)

# --- Load Model and Generate Response ---
llm = None # Initialize llm to None
try:
    # Load the model with verbose=False
    llm = Llama(model_path=gguf_model_path, verbose=False) # Key change: verbose=False
    # print("GGUF model loaded successfully.", file=sys.stderr) # Keep this on stderr or remove

    prompt = "Question: what should i eat if I have calcium deficiency? Answer:"
    # print(f"\nPrompt: {prompt}", file=sys.stderr) # Keep this on stderr or remove

    output = llm.create_completion(
        prompt,
        max_tokens=512,
        stop=["Question:", "\n\n"],
        temperature=0.7,
    )

    generated_text = output['choices'][0]['text']
    # Print ONLY the generated text to stdout
    print(generated_text)

except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1) # Exit if there's an error during generation

finally:
    if llm is not None:
        # print("\nModel resources will be released when script ends.", file=sys.stderr)
        pass

# print("\nScript finished.", file=sys.stderr) # Keep this on stderr or remove
