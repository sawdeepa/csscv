import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Define the model name for the main model
model_name = "Elixpo/LlamaMedicine"
# Define the model name for the tokenizer (fallback)
tokenizer_model_name = "hf-internal-testing/llama-tokenizer"

save_directory = "./LlamaMedicine_model_tokenizer"

# Create save directory if it doesn't exist
os.makedirs(save_directory, exist_ok=True)

print(f"Attempting to load model: {model_name} (without quantization)")
print(f"Attempting to load tokenizer from: {tokenizer_model_name}")

try:
    # --- Step 1: Load the tokenizer ---
    print(f"Loading tokenizer from: {tokenizer_model_name}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_name, trust_remote_code=True)
        print("Tokenizer loaded successfully.")
    except Exception as e:
        print(f"Could not load tokenizer {tokenizer_model_name}. Error: {e}")
        raise e

    # --- Step 2: Load the model (without quantization) ---
    print(f"Loading model {model_name}...")
    # The Elixpo/LlamaMedicine config.json is very small (29 bytes).
    # This might not be enough for AutoModelForCausalLM to determine the architecture.
    # If this fails, it might be because the repo is primarily for GGUF.
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True, # In case of unusual model structure or config
        # device_map="auto" # Let transformers decide device, or remove if causing issues on CPU
    )
    print("Model loaded successfully.")

    # Determine device
    if torch.cuda.is_available():
        device = "cuda"
        model.to(device)
        print(f"Model moved to {device}.")
    else:
        device = "cpu"
        # If model is large, it might already be on CPU or this won't change much
        # For very large models, this might OOM on CPU.
        print(f"CUDA not available. Model is on {device}.")


    # --- Step 3: Save the model and tokenizer ---
    model.save_pretrained(os.path.join(save_directory, "model"))
    tokenizer.save_pretrained(os.path.join(save_directory, "tokenizer"))
    print(f"Model and tokenizer saved to {save_directory}")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()

print("Script finished.")
