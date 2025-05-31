from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import os

# --- Download Logic ---
# Define model details for download
repo_id_download = "Elixpo/LlamaMedicine"
filename_download = "unsloth.Q8_0.gguf"
download_dir = "./temp"
# This is the path where the file will be after download and potential rename
gguf_model_path = os.path.join(download_dir, "LlamaMedicine_unsloth.Q8_0.gguf")

# Create the download directory if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

# Check if model already exists, if not, download it
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

        # Expected final name for the downloaded file from hf_hub
        expected_hub_filename_in_dir = os.path.join(download_dir, filename_download)

        # Rename if the downloaded file name is not yet our target gguf_model_path
        if os.path.abspath(expected_hub_filename_in_dir) != os.path.abspath(gguf_model_path):
            print(f"File downloaded to {expected_hub_filename_in_dir}. Renaming to {gguf_model_path}.")
            os.rename(expected_hub_filename_in_dir, gguf_model_path)
        else:
            # This means hf_hub_download put it directly where gguf_model_path points,
            # possibly because filename_download was already "LlamaMedicine_unsloth.Q8_0.gguf"
            # or because gguf_model_path was constructed to match downloaded_path_from_hub.
            # The current logic has filename_download as "unsloth.Q8_0.gguf" and
            # gguf_model_path as "./temp/LlamaMedicine_unsloth.Q8_0.gguf", so a rename is expected.
            print(f"File downloaded as {expected_hub_filename_in_dir}, which is already the target path or was handled by prior logic.")


        if os.path.exists(gguf_model_path):
            print(f"Successfully downloaded model to {gguf_model_path}")
        else:
            print(f"Error: File still not found at {gguf_model_path} after download and rename attempt.")
            # Exit if download failed, as loading will fail
            exit()

    except Exception as e:
        print(f"An error occurred during model download: {e}")
        import traceback
        traceback.print_exc()
        # Exit if download failed
        exit()
else:
    print(f"Model file already exists at {gguf_model_path}. Skipping download.")

# --- Load Logic ---
print(f"Attempting to load GGUF model from: {gguf_model_path}")

try:
    llm = Llama(model_path=gguf_model_path, verbose=True)
    print("GGUF model loaded successfully into Llama from llama_cpp.")

except Exception as e:
    print(f"An error occurred while loading the GGUF model: {e}")
    import traceback
    traceback.print_exc()

print("Script finished.")
