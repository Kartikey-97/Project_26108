with open('frontend/src/pages/analysis/AnalysisGapsTab.tsx', 'r') as f:
    content = f.read()

import re

old_block_regex = r"  const \[decisions, setDecisions\] = useState<Record<string, HumanDecision>>\(\{[\s\S]*?\}\);"

new_block = """  const [decisions, setDecisions] = useState<Record<string, HumanDecision>>(() => {
    const saved = localStorage.getItem(`decisions-mock`);
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return {
      'req-sp-1': 'accepted',
      'req-sp-2': 'accepted',
      'req-sp-3': 'accepted',
      'req-sp-4': 'accepted',
      'req-sp-5': 'reviewed',
      'req-sp-6': 'reviewed',
      'req-sp-7': 'accepted',
      'req-sp-10': 'reviewed',
      'req-sp-11': 'accepted',
    };
  });

  useEffect(() => {
    localStorage.setItem(`decisions-mock`, JSON.stringify(decisions));
  }, [decisions]);"""

match = re.search(old_block_regex, content)
if match:
    content = content.replace(match.group(0), new_block)
    with open('frontend/src/pages/analysis/AnalysisGapsTab.tsx', 'w') as f:
        f.write(content)
    print("Fixed decisions state persistence")
else:
    print("Could not find block in AnalysisGapsTab.tsx")
