import os

def dump_dir(path, outfile, exclude_dirs=['.git', '.venv', 'node_modules', '__pycache__', 'dist', 'build', '.next']):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        for file in files:
            if file.startswith('.') or file.endswith(('.pyc', '.png', '.jpg', '.jpeg', '.svg', '.lock', '.log')):
                continue
            
            filepath = os.path.join(root, file)
            # Skip code_base.txt and dump_codebase.py
            if file in ['code_base.txt', 'dump_codebase.py']:
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                outfile.write(f"\n{'='*80}\n")
                outfile.write(f"FILE: {filepath}\n")
                outfile.write(f"{'='*80}\n")
                outfile.write(content)
                outfile.write("\n")
            except Exception as e:
                pass

with open('code_base.txt', 'w', encoding='utf-8') as f:
    dump_dir('.', f)
