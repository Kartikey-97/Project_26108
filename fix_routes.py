with open("backend/kartikey/api/routes/standards.py", "r") as f:
    lines = f.readlines()

out = []
bis_block = []
in_bis = False
for line in lines:
    if "@router.get(\"/bis-sync-status\")" in line:
        in_bis = True
    
    if in_bis:
        bis_block.append(line)
        if "return get_sync_status()" in line:
            in_bis = False
    else:
        out.append(line)

if bis_block:
    # insert before get_standard
    for i, line in enumerate(out):
        if "@router.get(\"/{standard_id}\")" in line:
            out = out[:i] + bis_block + ["\n"] + out[i:]
            break

with open("backend/kartikey/api/routes/standards.py", "w") as f:
    f.writelines(out)

