import os
import shutil

def extract_python_code(output_file, ignore_folders = [".venv", "__pycache__"]):
    """
    This function extracts the content of all .py files 
    in the current directory and its subdirectories,
    ignoring the script itself and the specified folders, 
    and appends them to an output text file. 
    It also includes a tree structure of the directory.

    Args:
      output_file: The path to the output text file.
      ignore_folders: A list of folders to ignore.
    """

    try:
        with open(output_file, 'a', encoding='utf-8') as outfile:
            current_dir = os.getcwd()

            # Add the directory tree structure to the output file
            outfile.write(f"**Directory Tree:**\n")
            for root, dirs, files in os.walk(current_dir):
                # Filter out ignored folders
                new_dirs = []
                for d in dirs:
                    if d not in ignore_folders:
                        new_dirs.append(d)
                dirs[:] = new_dirs  # Update the dirs list with the filtered folders

                # Build the directory tree
                level = root.replace(current_dir, '').count(os.sep)
                indent = '  ' * level
                outfile.write(f"{indent}{os.path.basename(root)}\n")
                for filename in files:
                    if filename.endswith(".py") and filename != "extract_code.py":
                        file_path = os.path.join(root, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                # Add the code with the file name and directory level
                                outfile.write(f"{indent}**{filename}**\n{content}\n\n")
                                print(f"Extracted code from: {file_path}")
                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    output_file_path = "extracted_code.txt"
    ignore_folders = [".venv", "__pycache__"]  # Add folders to ignore

    extract_python_code(output_file_path, ignore_folders)
    print("Code extraction completed!")