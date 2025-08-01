import zipfile
import shutil
from pathlib import Path

PREFIX_LOCAL = Path("R:/GitHub/").resolve().as_posix()  # exact prefix to strip
PAGES_BASE = "https://flexfactorvu.github.io/"

def zip_directory(source_dir: Path, zip_path: Path, exclude_files=None, skip_root_files: bool = False):
    if exclude_files is None:
        exclude_files = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in source_dir.rglob("*"):
            if path.is_file():
                if skip_root_files and path.parent == source_dir:
                    continue
                if path.name in exclude_files:
                    continue
                zipf.write(path, arcname=path.relative_to(source_dir))

def url_from_local(path: Path) -> str:
    # convert absolute path to GitHub Pages URL by replacing the fixed local prefix
    p = path.resolve().as_posix()
    if not p.startswith(PREFIX_LOCAL):
        # fallback: still try to do naive replacement of drive letter style
        # strip first len(PREFIX_LOCAL) chars anyway
        tail = p[len(PREFIX_LOCAL):]
    else:
        tail = p[len(PREFIX_LOCAL):]
    # ensure no leading slash duplication
    if tail.startswith("/"):
        tail = tail[1:]
    # escape spaces only
    tail = tail.replace(" ", "%20")
    return PAGES_BASE + tail

def generate_imvu_seo_description():
    current_dir = Path(".").resolve()
    folder_name = current_dir.name
    script_name = Path(__file__).name

    # main zip
    main_zip_name = f"{folder_name}_all_files.zip"
    zip_directory(current_dir, current_dir / main_zip_name, exclude_files=[script_name], skip_root_files=True)

    section_blocks = []
    for folder in sorted(current_dir.iterdir()):
        if not folder.is_dir():
            continue
        image_files = sorted([f for f in folder.glob("*") if f.suffix.lower() in [".png", ".jpg", ".jpeg"]])
        if not image_files:
            continue

        # zip this section (images only)
        zip_name = f"{folder_name}_{folder.name}.zip"
        temp = folder.parent / f"_{folder.name}_temp"
        if temp.exists():
            shutil.rmtree(temp)
        shutil.copytree(folder, temp)
        for f in list(temp.iterdir()):
            if f.is_file() and f.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
                f.unlink()
        zip_directory(temp, current_dir / zip_name, skip_root_files=False)
        shutil.rmtree(temp)

        display_name = folder.name.replace("_", " ").title()
        section_zip_url = url_from_local(current_dir / zip_name)

        block = (
            f'\n  <div class="section">\n'
            f'    <div class="section-title">{display_name}</div>\n'
            f'    <div class="download-all">\n'
            f'      <a href="{section_zip_url}" class="download-button" target="_blank">Download All {display_name}</a>\n'
            f'    </div>\n'
            f'    <div class="image-grid">\n'
        )
        for img in image_files:
            img_url = url_from_local(folder / img.name)
            block += f'      <a href="{img_url}" target="_blank"><img src="{img_url}" class="texture-img"></a>\n'
        block += "    </div>\n  </div>\n"
        section_blocks.append(block)

    all_files_url = url_from_local(current_dir / main_zip_name)

    html = (
        f'<!DOCTYPE html>\n'
        f'<html>\n'
        f'<head>\n'
        f'  <meta charset="UTF-8">\n'
        f'  <title>{folder_name}</title>\n'
        f'  <style>\n'
        f'    body {{ background-color: #000; color: #ffa500; font-family: Arial, sans-serif; text-align: center; padding: 30px; }}\n'
        f'    .thank-you {{ font-size: 12px; margin-bottom: 10px; }}\n'
        f'    .brand-title {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }}\n'
        f'    .subtext {{ font-size: 14px; font-style: italic; margin-bottom: 20px; }}\n'
        f'    .hidden-keywords {{ display: none; }}\n'
        f'    .title {{ font-size: 24px; margin: 10px 0; }}\n'
        f'    .disclaimer {{ font-size: 14px; margin: 10px 0 20px; }}\n'
        f'    .download-all {{ display: block; text-align: center; margin-bottom: 20px; }}\n'
        f'    .download-button {{ background-color: transparent; color: #ffa500; border: 2px solid #ffa500; padding: 10px 20px; font-size: 14px; font-family: "Arial Black", Gadget, sans-serif; text-decoration: none; transition: background-color 0.3s, color 0.3s; cursor: pointer; display: inline-block; }}\n'
        f'    .download-button:hover {{ background-color: #ffa500; color: #000; }}\n'
        f'    .image-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; justify-content: center; max-width: 800px; margin: 0 auto; }}\n'
        f'    .texture-img {{ width: 128px; height: 256px; object-fit: contain; background-color: #808080; border-radius: 4px; padding: 4px; transition: transform 0.2s ease-in-out; }}\n'
        f'    .texture-img:hover {{ transform: scale(1.15); z-index: 1; }}\n'
        f'  </style>\n'
        f'</head>\n'
        f'<body>\n'
        f'  <div class="thank-you">thank you for shopping</div>\n'
        f'  <div class="brand-title">F L E X F A C T O R</div>\n'
        f'  <div class="subtext">try before you buy!</div>\n'
        f'  <div class="hidden-keywords">emo goth y2k muscle hot daddy</div>\n'
        f'  <div class="title">{folder_name}</div>\n'
        f'  <div class="disclaimer">Use of my textures is only allowed for products derived from me.<br>You CAN make your product derivable as well.<br>However, omitting me from the derivation chain while using my textures or ripping and reuploading my mesh will result in a DMCA takedown.</div>\n'
        f'  <div class="all-files-button">\n'
        f'    <a href="{all_files_url}" class="download-button" target="_blank">Download All Files</a>\n'
        f'  </div>\n'
        f'{"".join(section_blocks)}\n'
        f'</body>\n'
        f'</html>\n'
    )

    (current_dir / "imvu_description.html").write_text(html, encoding="utf-8")
    print("generated imvu_description.html at", current_dir / "imvu_description.html")

if __name__ == "__main__":
    generate_imvu_seo_description()
