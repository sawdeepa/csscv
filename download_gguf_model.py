from huggingface_hub import hf_hub_download
import os

# Define model details
repo_id = "Elixpo/LlamaMedicine"
filename = "unsloth.Q8_0.gguf"

# Define a directory that should be gitignored
download_dir = "./temp"
local_save_path = os.path.join(download_dir, "LlamaMedicine_unsloth.Q8_0.gguf")

# Create the download directory if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

print(f"Starting download of {filename} from {repo_id} to {local_save_path}...")

try:
    # Download the file directly into the target directory
    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=download_dir, # Download into the 'temp' directory
        local_dir_use_symlinks=False, # Ensure the actual file is there
        # force_download=True # Uncomment to force download even if file exists
    )

    # hf_hub_download will save the file as <local_dir>/<filename_on_hub> if filename is simple
    # or into a snapshot structure if filename is a path within the repo.
    # For a top-level file like "unsloth.Q8_0.gguf", it should be <local_dir>/unsloth.Q8_0.gguf

    # The returned 'downloaded_path' is the actual path to the downloaded file.
    # We want to ensure it's at local_save_path.
    # If hf_hub_download saved it directly as local_dir/filename, then downloaded_path should be local_save_path.

    expected_downloaded_file_location = os.path.join(download_dir, filename)

    if os.path.abspath(downloaded_path) != os.path.abspath(local_save_path):
        # This might happen if local_save_path was different from download_dir/filename,
        # or if hf_hub_download created a snapshot structure.
        # For this script, local_save_path IS download_dir/filename.
        # However, if filename on hub was different, or we wanted a different local name,
        # os.rename would be needed.
        # Given current setup, this rename should ideally not be necessary if downloaded_path is already correct.
        print(f"File downloaded to {downloaded_path}. Ensuring it is at {local_save_path}.")
        if os.path.exists(local_save_path) and os.path.abspath(downloaded_path) != os.path.abspath(local_save_path):
             os.remove(local_save_path) # Remove if it's a different file (e.g. from previous failed run)
        if os.path.abspath(downloaded_path) != os.path.abspath(local_save_path):
             os.rename(downloaded_path, local_save_path)
    else:
        print(f"File downloaded to and located at: {local_save_path}")


    # Confirm the file exists at the target path
    if os.path.exists(local_save_path):
        file_size = os.path.getsize(local_save_path)
        print(f"Successfully downloaded and confirmed file: {local_save_path}")
        print(f"File size: {file_size / (1024*1024):.2f} MB")
    else:
        # This case should ideally not happen if hf_hub_download succeeded and rename (if any) worked.
        print(f"Error: File not found at {local_save_path} (downloaded_path was {downloaded_path}).")
        # Check if it's at the direct download location before any rename logic was attempted
        if os.path.exists(expected_downloaded_file_location):
            print(f"However, file IS present at {expected_downloaded_file_location}. The rename/move logic might have an issue.")
        else:
            print(f"File is also NOT present at {expected_downloaded_file_location}.")


except Exception as e:
    print(f"An error occurred during download: {e}")
    import traceback
    traceback.print_exc()

print("Script finished.")
