import sys
sys.path.append('backend')
from kartikey.orchestration.knowledge_registry import initialize_knowledge_registry
registry = initialize_knowledge_registry()
print("Success!")
