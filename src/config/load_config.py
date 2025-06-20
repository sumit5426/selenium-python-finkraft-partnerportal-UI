import os
import yaml
from dotenv import load_dotenv
import re

# Load .env
load_dotenv()

# Get absolute path to config.yaml (safe & correct)
current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(current_dir, "config.yaml")

# Load YAML
with open(yaml_path, "r") as file:
    raw_config = yaml.safe_load(file)

# Replace ${ENV_VAR} with actual env values
def substitute_env_vars(data):
    if isinstance(data, dict):
        return {k: substitute_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_env_vars(i) for i in data]
    elif isinstance(data, str):
        return re.sub(r"\$\{([^}]+)\}", lambda m: os.getenv(m.group(1), ""), data)
    else:
        return data

config = substitute_env_vars(raw_config)

# Example usage
print(config["environments"]["QA"]["clients"]["YATRA"]["username"])
