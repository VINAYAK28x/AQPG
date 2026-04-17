%%capture
# Cell 1: Install Unsloth and dependencies cleanly
!pip install "unsloth[kaggle-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps xformers trl peft accelerate bitsandbytes # Cell 3: Load Model and Tokenizer via Unsloth
from unsloth import FastLanguageModel
import torch

max_seq_length = 1024 # Mistral can handle longer context, but 1024 keeps it fast
dtype = None          
load_in_4bit = True   # CRITICAL: 4bit quantization to save memory

# We use the unsloth pre-quantized mistral model for much faster downloading
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/mistral-7b-instruct-v0.2-bnb-4bit", 
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

print(f"GPU memory used: {torch.cuda.memory_allocated()/1e9:.2f} GB") # Cell 4: Apply LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, 
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, 
    bias = "none",    
    use_gradient_checkpointing = "unsloth", 
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)# Cell 5: Load and Prepare Dataset
from datasets import load_dataset

# 🛑 REPLACE this path with the exact path from Cell 2!
dataset_path = "/kaggle/input/datasets/sanamikaajith/pyq-mistral-train-jsonl/pyq_mistral_train.jsonl"

dataset = load_dataset("json", data_files=dataset_path, split="train")

# Your dataset already has a perfectly formatted "text" column!
dataset = dataset.select_columns(["text"])

# Split into train and validation
dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = dataset["train"]
val_dataset = dataset["test"]

print(f"Training samples: {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")# Cell 6: Train and Save Model (OOM FIX)
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported
import json

# --- MEMORY FIXES APPLIED HERE ---
training_args = TrainingArguments(
    per_device_train_batch_size = 1,      # ⬅️ Reduced from 2 to 1 to save massive memory
    gradient_accumulation_steps = 8,      # ⬅️ Increased to 8 to maintain effective batch size
    warmup_steps = 10,
    num_train_epochs = 1, 
    learning_rate = 2e-4,
    fp16 = not is_bfloat16_supported(),
    bf16 = is_bfloat16_supported(),
    logging_steps = 10,
    optim = "adamw_8bit",
    weight_decay = 0.01,
    lr_scheduler_type = "linear",
    seed = 3407,
    output_dir = "mistral_outputs",
    report_to="none",
    average_tokens_across_devices = False,
)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_dataset,
    eval_dataset = val_dataset,
    dataset_text_field = "text",
    max_seq_length = 512,                 # ⬅️ Reduced from 1024 to 512. Your dataset easily fits in 512!
    dataset_num_proc = 2,
    args = training_args,
)

print("Starting Mistral training...")
trainer_stats = trainer.train()
print("Training finished!")

# --- SAVING THE MODEL ---
save_name = "mistral_7b_pyq_lora_v1"

print(f"Saving LoRA adapters locally to {save_name}...")
model.save_pretrained(save_name) 
tokenizer.save_pretrained(save_name)

# Create dataset metadata for Kaggle upload
print("Creating Kaggle dataset metadata...")
meta = {
    "title": "mistral-7b-pyq-lora-v1",
    "id": f"sanamikaajith/mistral-7b-pyq-lora-v1", 
    "licenses": [{"name": "CC0-1.0"}]
}

with open(f"/kaggle/working/{save_name}/dataset-metadata.json", "w") as f:
    json.dump(meta, f)

print("Uploading to Kaggle datasets permanently...")
!kaggle datasets create -p /kaggle/working/{save_name} --dir-mode zip
print("Model LoRA adapters saved successfully!"). ithayirunu training script aake 10 minute eduthullu train chaeyan ithu sheriyaano?