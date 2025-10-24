import os

def load_instructions_from_file(
    filename: str, default_instruction: str = "Default instruction."
) -> str:
    """Load instructions from a given file."""
    instruction = default_instruction

    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "r", encoding="utf-8") as file:
            instructions = file.read()
        print(f"Successfully loaded instructions from {filename}")
    except FileNotFoundError:
        print("WARNING: Instruction file not found. Using default.")
    except Exception as e:
        print("ERROR loading instruction file {filename}: {e}. Using default.")
    return instructions
