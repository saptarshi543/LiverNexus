import os

def fix_encoding(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                path = os.path.join(dirpath, fname)
                content = None
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeError:
                    print(f"Fixing encoding for {path}")
                    try:
                        with open(path, 'r', encoding='utf-16') as f:
                            content = f.read()
                    except UnicodeError:
                        print(f"Failed to read {path} as utf-16 too.")
                
                if content is not None:
                    # Write back as utf-8
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)

if __name__ == "__main__":
    fix_encoding("backend")
    print("Encoding fix complete.")
