import json
import os

# Load a JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Recursive function to compare two JSON objects
def compare_json(json1, json2, path=""):
    differences = []

    if isinstance(json1, dict) and isinstance(json2, dict):
        keys1 = set(json1.keys())
        keys2 = set(json2.keys())

        if path == "":
            # At the root level, compare top-level keys
            for key in keys1 - keys2:
                differences.append(f"Top-level key '{key}' missing in second JSON")
            for key in keys2 - keys1:
                differences.append(f"Top-level key '{key}' missing in first JSON")

            # If both have only one key, and keys are different, report the mismatch and compare their values
            if len(keys1) == 1 and len(keys2) == 1:
                key1 = next(iter(keys1))
                key2 = next(iter(keys2))
                if key1 != key2:
                    differences.append(f"Top-level key mismatch: '{key1}' vs '{key2}'")
                # Compare the values under these keys
                differences.extend(compare_json(json1[key1], json2[key2], f"{key1}/{key2}"))
            else:
                # For keys present in both JSONs, compare their values
                common_keys = keys1 & keys2
                for key in common_keys:
                    differences.extend(compare_json(json1[key], json2[key], key))
        else:
            # Not at the root level, proceed as usual
            all_keys = keys1.union(keys2)
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key in json1 and key in json2:
                    differences.extend(compare_json(json1[key], json2[key], new_path))
                elif key in json1:
                    differences.append(f"Key '{new_path}' missing in second JSON")
                else:
                    differences.append(f"Key '{new_path}' missing in first JSON")
    elif isinstance(json1, list) and isinstance(json2, list):
        min_len = min(len(json1), len(json2))
        for i in range(min_len):
            new_path = f"{path}[{i}]"
            differences.extend(compare_json(json1[i], json2[i], new_path))
        # Check for extra elements
        if len(json1) > len(json2):
            for i in range(min_len, len(json1)):
                new_path = f"{path}[{i}]"
                differences.append(f"Extra element in first JSON at '{new_path}': {json1[i]}")
        elif len(json2) > len(json1):
            for i in range(min_len, len(json2)):
                new_path = f"{path}[{i}]"
                differences.append(f"Extra element in second JSON at '{new_path}': {json2[i]}")
    else:
        # Direct comparison
        if json1 != json2:
            differences.append(f"Value mismatch at '{path}': '{json1}' vs '{json2}'")

    return differences

# Compare multiple files and log differences
def compare_multiple_jsons(files):
    if len(files) < 2:
        print("Please provide at least two files for comparison.")
        return

    differences = []

    # Compare each file against the first one
    base_file = files[0]
    base_json = load_json(base_file)

    for other_file in files[1:]:
        other_json = load_json(other_file)
        diff = compare_json(base_json, other_json)
        if diff:
            differences.append((base_file, other_file, diff))

    # Save differences to a file
    output_file = "differences.txt"
    with open(output_file, "w") as f:
        for base, other, diff in differences:
            f.write(f"Differences between {os.path.basename(base)} and {os.path.basename(other)}:\n")
            for d in diff:
                f.write(f"  {d}\n")
            f.write("\n")

    print(f"Differences saved to {output_file}")

# File paths (Replace with actual paths to your JSON files)
files = ["file1.json", "file2.json"]

# Compare and log differences
compare_multiple_jsons(files)
