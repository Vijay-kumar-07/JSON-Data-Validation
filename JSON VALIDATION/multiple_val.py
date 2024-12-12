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
                differences.append(f"Top-level key '{key}' missing in target JSON")
            for key in keys2 - keys1:
                differences.append(f"Top-level key '{key}' missing in source JSON")

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
                    differences.append(f"Key '{new_path}' missing in target JSON")
                else:
                    differences.append(f"Key '{new_path}' missing in source JSON")
    elif isinstance(json1, list) and isinstance(json2, list):
        min_len = min(len(json1), len(json2))
        for i in range(min_len):
            new_path = f"{path}[{i}]"
            differences.extend(compare_json(json1[i], json2[i], new_path))
        # Check for extra elements
        if len(json1) > len(json2):
            for i in range(min_len, len(json1)):
                new_path = f"{path}[{i}]"
                differences.append(f"Extra element in source JSON at '{new_path}': {json1[i]}")
        elif len(json2) > len(json1):
            for i in range(min_len, len(json2)):
                new_path = f"{path}[{i}]"
                differences.append(f"Extra element in target JSON at '{new_path}': {json2[i]}")
    else:
        # Direct comparison
        if json1 != json2:
            differences.append(f"Value mismatch at '{path}': '{json1}' vs '{json2}'")

    return differences

# Compare files in two directories and log differences
def compare_directories(source_dir, target_dir):
    source_files = set(os.listdir(source_dir))
    target_files = set(os.listdir(target_dir))

    all_files = source_files.union(target_files)

    # Open the output file once and append to it
    output_file = "differences.txt"
    with open(output_file, "w") as f_output:
        for filename in sorted(all_files):
            source_file_path = os.path.join(source_dir, filename)
            target_file_path = os.path.join(target_dir, filename)

            if filename in source_files and filename in target_files:
                try:
                    source_json = load_json(source_file_path)
                    target_json = load_json(target_file_path)

                    differences = compare_json(source_json, target_json)

                    if differences:
                        f_output.write(f"Differences between '{filename}' in source and target directories:\n")
                        for diff in differences:
                            f_output.write(f"  {diff}\n")
                    else:
                        f_output.write(f"No differences found for '{filename}'.\n")

                except json.JSONDecodeError as e:
                    f_output.write(f"Error decoding JSON for file '{filename}': {e}\n")
                except Exception as e:
                    f_output.write(f"Error processing file '{filename}': {e}\n")
            elif filename in source_files:
                f_output.write(f"File '{filename}' is missing in target directory.\n")
            else:
                f_output.write(f"File '{filename}' is missing in source directory.\n")

            # Add three empty lines between file comparisons
            f_output.write("\n\n\n")

    print(f"Differences saved to {output_file}")

# Paths to the source and target directories (replace with your actual paths)
source_directory = "source"
target_directory = "target"

# Compare the directories and log differences
compare_directories(source_directory, target_directory)
