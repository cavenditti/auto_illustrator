import os
import subprocess
from urllib.parse import quote
from glob import glob
import pandas as pd

from PIL import Image


PICTURES_DIR = "pictures"
SOURCE_FILE = "sources/Cards.xlsx"
SOURCE_SHEET = "Creatures"
TEMPLATE_PREFIX = "creature"
OUT_DIR = "output"

# This are the dimensions of the final grid, tune to your needs.
# For tabletop simulator this is problably fine for most cases
GRID_SIZE = (10, 7)

# map SVG template fields to Excel file rows
REPLACEMENT_TEMPLATE = {
    "name": "Name",
    "description": "Description",
    "b": "B",
    "m": "M",
    "effect_1": "Effect L",
    "sym_1": "Sym L",
    "effect_2": "Effect R",
    "sym_2": "Sym R",
}


def angular_template(replacements: dict) -> dict:
    return {f"&lt;{k}&gt;": v for k, v in replacements.items()}


def add_image_replacement(replacements, image_path):
    # This is the path of the image you used in your SVG file. Note that this is url-encoded
    template_image_path = "./PICTURE%20PATH%20IN%20YOUR%20SVG%20FILE.webp"

    image_path = os.path.join(PICTURES_DIR, quote(image_path))
    print(image_path, os.path.exists(image_path))
    replacements[template_image_path] = os.path.abspath(image_path)


def fill_template(source_path, destination_path, replacements):
    # Read the source file
    with open(source_path, "r") as file:
        content = file.read()

    # Replace template fields
    for key, value in replacements.items():
        content = content.replace(key, value)

    # Write to the new file
    with open(destination_path, "w") as file:
        file.write(content)


def make_card(template: str, replacements: dict, image: str):
    outfile = os.path.join(OUT_DIR, "SVGs", replacements["name"] + ".svg")

    # we have everything between "<>" and escaped in the template
    replacements = angular_template(replacements)

    # Prepare image replacement
    add_image_replacement(replacements, image)

    # Fill the template
    fill_template(os.path.join("templates", template), outfile, replacements)


def convert_svg_to_png(svg_file, png_file):
    # Command to convert SVG to PNG using Inkscape
    command = [
        "inkscape",
        svg_file,
        "--export-type=png",
        "--export-filename=" + png_file,
    ]
    subprocess.run(command)


def merge_images_into_grid(image_files, grid_size=(10, 10), image_size=(100, 100)):
    # Create a new image with a white background
    grid_image = Image.new(
        "RGB", (image_size[0] * grid_size[0], image_size[1] * grid_size[1]), "white"
    )

    for index, file in enumerate(image_files):
        # Open the image
        img = Image.open(file)
        # Resize image if it's not the desired size
        img = img.resize(image_size)

        # Calculate position
        x = index % grid_size[0] * image_size[0]
        y = index // grid_size[0] * image_size[1]

        # Paste the image into the grid
        grid_image.paste(img, (x, y))

    return grid_image


def example():
    # Define your replacements here
    template = "creature_light.svg"

    replacements = {
        "name": "Name",
        "description": "Some description",
        "b": "2",
        "m": "4",
        "effect_1": "EFFECT X",
        "sym_1": "",
        "effect_2": "EFFECT Y",
        "sym_2": "",
    }

    image = replacements["name"] + ".webp"

    make_card(template, replacements, image)


def fill_templates_from_xlsx(path: str, sheet: str, template_prefix: str):
    df = pd.read_excel(path, sheet)

    def fix_float(value):
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return str(int(value))
        return str(value)

    num_rows = len(df)
    if num_rows > GRID_SIZE[0] * GRID_SIZE[1]:
        print(
            f"WARNING: you have more cards ({num_rows}) to create than your GRID_SIZE ({GRID_SIZE}) can accomodate. Change GRID_SIZE and retry."
        )

    for __i, row in df.iterrows():
        template = f"{template_prefix}_{row['Template']}.svg"

        # create replacements
        replacements = {k: fix_float(row[v]) for k, v in REPLACEMENT_TEMPLATE.items()}

        image = replacements["name"] + ".webp"

        make_card(template, replacements, image)


def main():
    # create required output directories
    paths = ["SVGs", "PNGs"]
    for p in paths:
        os.makedirs(os.path.join(OUT_DIR, p), exist_ok=True)

    fill_templates_from_xlsx(SOURCE_FILE, SOURCE_SHEET, TEMPLATE_PREFIX)

    svg_files = glob(os.path.join(OUT_DIR, "SVGs", "*.svg"))
    png_files = []

    # Convert all SVG files to PNG
    for svg_file in svg_files:
        png_file = svg_file.replace("SVGs", "PNGs").replace(".svg", ".png")
        convert_svg_to_png(svg_file, png_file)
        png_files.append(png_file)

    assert png_files
    bb = Image.open(png_files[0]).getbbox()
    assert bb
    image_size = (bb[2] - bb[0], bb[3] - bb[1])

    # Merge PNG files into a single grid image
    grid_image = merge_images_into_grid(
        png_files, grid_size=GRID_SIZE, image_size=image_size
    )
    grid_image.save(
        os.path.join(OUT_DIR, "merged_grid.png")
    )  # Save the final grid image


if __name__ == "__main__":
    main()
