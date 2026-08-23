import os

def generate_codebase(root_dir, output_file, extensions=('.py', '.js', '.jsx', '.json', '.md')):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_dir):
            if any(x in root for x in ['venv', 'node_modules', '.git', '__pycache__', '.venv', 'uploads']):
                continue
            for file in files:
                if file == "code_base.txt" or file.endswith("lock.json"): continue
                if file.endswith(extensions):
                    filepath = os.path.join(root, file)
                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f"FILE: {filepath}\n")
                    outfile.write(f"{'='*80}\n\n")
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]\n")

if __name__ == "__main__":
    generate_codebase('.', 'code_base.txt')
