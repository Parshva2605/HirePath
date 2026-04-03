"""
Quick Model Switcher for GitHub Profile Analyzer
Run this to easily change which LLM model to use
"""

import os

AVAILABLE_MODELS = {
    "1": ("qwen3:8b", "Recommended - Latest, best reasoning (5.2GB)"),
    "2": ("mashriram/sarvam-1:latest", "Faster, smaller model (1.5GB)"),
    "3": ("llava-llama3:8b", "LLaMA 3 based (5.5GB)"),
    "4": ("llava:13b", "Larger model, more capable (8GB)"),
}

print("="*70)
print("  GITHUB ANALYZER - MODEL SWITCHER")
print("="*70)
print()
print("Available LLM models on your system:")
print()

for key, (model, desc) in AVAILABLE_MODELS.items():
    print(f"{key}. {model}")
    print(f"   {desc}")
    print()

print("Current .env configuration:")
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('OLLAMA_MODEL='):
                current = line.split('=')[1].strip()
                print(f"   OLLAMA_MODEL={current}")
                break
else:
    print("   .env file not found!")
    print()
    choice = input("Would you like to create it now? (y/n): ")
    if choice.lower() == 'y':
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("   ✓ Created .env from .env.example")
        else:
            print("   ✗ .env.example not found")

print()
print("-"*70)
choice = input("\nEnter model number to switch (or 'q' to quit): ").strip()

if choice in AVAILABLE_MODELS:
    model_name, _ = AVAILABLE_MODELS[choice]
    
    if os.path.exists(env_path):
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update OLLAMA_MODEL line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('OLLAMA_MODEL='):
                lines[i] = f'OLLAMA_MODEL={model_name}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'\nOLLAMA_MODEL={model_name}\n')
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        print()
        print("="*70)
        print(f"✓ Successfully switched to: {model_name}")
        print("="*70)
        print()
        print("Restart the application for changes to take effect:")
        print("  python app/main.py")
    else:
        print("\n✗ .env file not found. Please create it first.")
        
elif choice.lower() != 'q':
    print("\n✗ Invalid choice. No changes made.")
else:
    print("\nNo changes made.")
