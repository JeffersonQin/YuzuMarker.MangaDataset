import json
import os


# path of the script
script_path = os.path.dirname(os.path.realpath(__file__))
# path of the data folder
gallery_path = os.path.join(script_path, "..", "gallery-dl")


# walk through the data folder and check for all json files
def get_files(path):
    all_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    return all_files


for file in get_files(gallery_path):
    with open(file, "r") as f:
        data = json.load(f)
        if "imageData" in data.keys():
            data["imageData"] = None

    with open(file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
