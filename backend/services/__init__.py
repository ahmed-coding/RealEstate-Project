import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
print(f"Added {str(Path(__file__).parent)} to sys.path in services __init__.py")