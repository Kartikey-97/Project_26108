import re

def extract():
    transcript_file = r"C:\Users\krishna\.gemini\antigravity-ide\brain\92877cc2-84f0-48ca-9fa9-9c9659c0a78a\.system_generated\logs\transcript_full.jsonl"
    with open(transcript_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    idx = content.find(r'[\n  {\n    \"is_number\":')
    if idx == -1:
        idx = content.find('[\n  {\n    "is_number":')
        
    if idx != -1:
        j_str = content[idx:]
        end_idx = j_str.rfind(']')
        if end_idx != -1:
            j_str = j_str[:end_idx+1]
            # Replace escaped newlines if any
            j_str = j_str.replace('\\n', '\n').replace('\\"', '"')
            # But wait, it might be inside a JSON string in the jsonl.
            with open('d:/ai_engine_SIH/data/Standard.json', 'w', encoding='utf-8') as out_f:
                out_f.write(j_str)
            print("Extracted successfully. Length:", len(j_str))
            return
            
    # Try finding the exact string
    import json
    for line in content.split('\n'):
        if not line.strip(): continue
        try:
            obj = json.loads(line)
            if obj.get('type') == 'USER_INPUT':
                text = obj.get('content', '')
                if isinstance(text, list):
                    for item in text:
                        if isinstance(item, dict) and 'text' in item:
                            val = item['text']
                            start = val.find('[\n  {\n    "is_number"')
                            if start != -1:
                                end = val.rfind(']')
                                with open('d:/ai_engine_SIH/data/Standard.json', 'w', encoding='utf-8') as out_f:
                                    out_f.write(val[start:end+1])
                                print("Extracted from list text!")
                                return
                elif isinstance(text, str):
                    start = text.find('[\n  {\n    "is_number"')
                    if start != -1:
                        end = text.rfind(']')
                        with open('d:/ai_engine_SIH/data/Standard.json', 'w', encoding='utf-8') as out_f:
                            out_f.write(text[start:end+1])
                        print("Extracted from string content!")
                        return
        except Exception as e:
            print("Error parsing line", e)
            
    print("Not found.")

extract()
