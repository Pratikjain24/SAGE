import zipfile, json, os, shutil
from pathlib import Path

dl = Path(r"C:\Users\kruti\Downloads")

def update_manifest_and_notes(zip_path: Path, new_archetype_name: str):
    if not zip_path.exists():
        print(f"File not found: {zip_path}")
        return
    print(f"Updating {zip_path.name} -> archetype_name: '{new_archetype_name}'")
    temp_zip = zip_path.with_suffix(".tmp.zip")
    
    with zipfile.ZipFile(zip_path, "r") as zin, zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename in ("FREEZE_MANIFEST.json", "state/FREEZE_MANIFEST.json"):
                try:
                    data = json.loads(content.decode("utf-8"))
                    data["archetype_name"] = new_archetype_name
                    content = json.dumps(data, indent=2).encode("utf-8")
                except Exception as e:
                    print(f"Error parsing {item.filename}: {e}")
            elif item.filename == "notes.txt":
                try:
                    text = content.decode("utf-8")
                    lines = text.splitlines()
                    new_lines = []
                    for l in lines:
                        if l.startswith("Assigned Layer :"):
                            grp = l.split(":")[1].split("(")[0].strip()
                            new_lines.append(f"Assigned Layer : {grp} ({new_archetype_name})")
                        else:
                            new_lines.append(l)
                    content = "\n".join(new_lines).encode("utf-8") + b"\n"
                except Exception as e:
                    print(f"Error parsing notes.txt: {e}")
            zout.writestr(item, content)
            
    if temp_zip.exists():
        if zip_path.exists():
            os.remove(zip_path)
        shutil.move(str(temp_zip), str(zip_path))
        print(f"✓ Successfully updated {zip_path.name}")

if __name__ == "__main__":
    # Update G6 archives: G6 is Oracle
    for g6_file in [dl / "G6_seeds42-46.zip", dl / "G6_seeds42-46 (1).zip"]:
        update_manifest_and_notes(g6_file, "Oracle Skyline")

    # Update G7 archives: G7 is Proxy Canary
    for g7_file in [dl / "G7_seeds42-46.zip", dl / "G7_seeds42-46(1).zip"]:
        update_manifest_and_notes(g7_file, "Proxy Canary Guard")
