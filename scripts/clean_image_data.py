import git
import json
import subprocess
import os


# path of the script
script_path = os.path.dirname(os.path.realpath(__file__))
# path of the data folder
repo_path = os.path.join(script_path, "..")


def git_diff():
    return [item.a_path for item in git.Repo(repo_path).index.diff(None)]


print(git_diff())

for file in git_diff():
    if str(file).startswith("gallery-dl/") and str(file).endswith(".json"):
        with open(file, "r") as f:
            data = json.load(f)
            if "imageData" in data.keys():
                data["imageData"] = None

        with open(file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        subprocess.run(["git", "add", file], check=True)
