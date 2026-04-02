import json
import os

def add_element_to_json_list(filename, key, element):
    if not os.path.isfile(filename):
        with open(filename, 'w', encoding = "utf-8") as file:
            file.write("{}")
    with open(filename, 'r', encoding = "utf-8") as file:
        data = json.load(file)

    if key in data:       
        print("Alias already occupied")
    else:
        data[key] = element

    with open(filename, 'w', encoding = "utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)