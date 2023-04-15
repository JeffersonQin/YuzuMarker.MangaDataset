import os
import os.path as osp
import json
import subprocess
import imgviz
import labelme
from PIL import Image
import numpy as np
import base64
import requests
import sys

class_names = ["text", "sfx"]

SERVER_URL = "http://yuzu-marker-manga-dataset-preview-server.vercel.app"
key = sys.argv[1]

# read .github/outputs/all_changed_files.json to get changed file list
with open(".github/outputs/all_changed_files.json", "r", encoding="utf-8") as f:
    file_list = json.load(f)

links = {}  # path to link

for file in file_list:
    if str(file).startswith("gallery-dl") and str(file).endswith(".json"):
        path = osp.dirname(file)
        if path not in links.keys():
            with open(osp.join(path, ".link"), "r") as f:
                links[path] = f.read().strip()


def encode_image(image_path, index):
    with open(image_path, "rb") as f:
        ext = image_path.split(".")[-1]
        content = base64.b64encode(f.read()).decode("utf-8")
        return {"ext": ext, "content": content, "index": index}


deploy_links = []

for path in links.keys():
    image_data = []

    link = links[path]
    subprocess.run(["gallery-dl", link], check=True)

    files = [
        osp.join(path, file) for file in os.listdir(path) if str(file).endswith(".json")
    ]
    files.sort()
    for i, filename in enumerate(files):
        print(f"Generating annotation from: {filename}")

        label_file = labelme.LabelFile(filename=filename)

        base = osp.splitext(osp.basename(filename))[0]
        out_viz_file = osp.join(path, base + "_annotated.jpg")

        img = np.array(Image.open(osp.join(path, label_file.imagePath)))

        bboxes = []
        labels = []

        for shape in label_file.shapes:
            if shape["shape_type"] != "rectangle":
                print(
                    "Skipping shape: label={label}, "
                    "shape_type={shape_type}".format(**shape)
                )
                continue

            (xmin, ymin), (xmax, ymax) = shape["points"]
            # swap if min is larger than max.
            xmin, xmax = sorted([xmin, xmax])
            ymin, ymax = sorted([ymin, ymax])

            bboxes.append([ymin, xmin, ymax, xmax])
            labels.append(int(shape["label"]) - 1)

        captions = [class_names[label] for label in labels]

        viz = imgviz.instances2rgb(
            image=img,
            labels=labels,
            bboxes=bboxes,
            captions=captions,
            font_size=15,
            line_width=2,
            colormap=np.array([[209, 65, 78], [57, 255, 156]]),
        )

        imgviz.io.imsave(out_viz_file, viz)

        image_data.append(encode_image(out_viz_file, i))

    response = requests.post(f"{SERVER_URL}/api/create", json={"key": key})
    if response.status_code == 200:
        uuid = response.json()["uuid"]
        print("Creation success!")
    else:
        print("Creation failed:", response.text)
        exit(1)

    for image in image_data:
        response = requests.post(
            f"{SERVER_URL}/api/upload", json={"image": image, "key": key, "uuid": uuid}
        )

        if response.status_code == 200:
            print("Images uploaded successfully!")
        else:
            print("Error uploading images:", response.text)
            exit(1)

    print(f"{SERVER_URL}/preview/{uuid}")
    deploy_links.append(f"{SERVER_URL}/preview/{uuid}")

print(f"::set-output name=deploy_links::{'%0A'.join(deploy_links)}")
