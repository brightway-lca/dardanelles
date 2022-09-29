import appdirs
import os
from pathlib import Path

def create_dir(dirpath):
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)


data_dir = Path(appdirs.user_data_dir("dardanelles", "dd"))
logs_dir = Path(appdirs.user_log_dir("dardanelles", "dd"))

(data_dir / "uploads").mkdir(parents=True, exist_ok=True)
logs_dir.mkdir(exist_ok=True)

print(f"dardanelles remote: Data directory is {data_dir}")
print(f"dardanelles remote: Log directory is {logs_dir}")
