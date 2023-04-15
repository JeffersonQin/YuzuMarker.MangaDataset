import git
import json
import subprocess
import os


# path of the script
script_path = os.path.dirname(os.path.realpath(__file__))
# path of the data folder
repo_path = os.path.join(script_path, "..")

repo = git.Repo(repo_path)


def git_in_index():
    return [item.a_path for item in repo.index.diff("HEAD")]


for file in git_in_index():
    if str(file).startswith("gallery-dl/") and str(file).endswith(".json"):
        if os.path.exists(file) is False:
            continue
        with open(file, "r") as f:
            data = json.load(f)
            if "imageData" in data.keys():
                data["imageData"] = None

        with open(file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        repo.index.add([file])
