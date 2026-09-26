import os

def generate_codebase(root_dir, output_file):
    valid_extensions = ('.py', '.ts', '.tsx', '.md')
    valid_jsons = ('package.json', 'tsconfig.json', 'mock_qco_database.json')
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_dir):
            if any(x in root for x in ['venv', 'node_modules', '.git', '__pycache__', '.venv', 'uploads', 'dist']):
                continue
            for file in files:
                if file in ["code_base.txt", "codebase.txt", "generate_codebase.py", "dump_codebase.py"]: continue
                
                include_file = False
                if file.endswith(valid_extensions):
                    include_file = True
                elif file.endswith('.json') and file in valid_jsons:
                    include_file = True
                    
                if include_file:
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
    generate_codebase('.', 'codebase.txt')
