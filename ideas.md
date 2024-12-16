# Ideas

## Model Selection
1. Llama 2 (7B) or Mistral (7B):
    - Why?
    - Small enough to run on mid-tier hardware (with quantization for lower memory usage).
    - High-quality outputs and supports fine-tuning or LoRA (Low-Rank Adaptation) for lightweight personalization.
    - Can easily be trained or prompted for specific tasks like generating questions in a pirate tone.

2. GPT-NeoX / GPT-J:
    - Why?
    - Open source and suitable for modest hardware.
    - GPT-J (6B) offers good trade-offs between capability and performance.
    - Trade-off: May require more customization for role-playing or generating creative questions.

3. FLAN-T5 (Small or Base):
    - Why?
    - Compact and efficient for inference.
    - Pre-trained on instruction-tuning tasks, making it adept at responding to prompts like, “Generate a question in a pirate tone.”