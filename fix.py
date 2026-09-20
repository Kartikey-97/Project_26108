with open("/Users/kartikeygupta/Desktop/Hackathons/sih_26108/frontend/src/pages/analysis/AnalysisRelationshipsTab.tsx", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "<div className=\"space-y-4\">" in line and "1. RELATIONSHIP SUMMARY METRIC STRIP" in lines[lines.index(line)+2]:
        break # Skip the rest of the file which is the old force graph!
    new_lines.append(line)

new_lines.append("}\n") # Close the AnalysisRelationshipsTab component

with open("/Users/kartikeygupta/Desktop/Hackathons/sih_26108/frontend/src/pages/analysis/AnalysisRelationshipsTab.tsx", "w") as f:
    f.writelines(new_lines)
