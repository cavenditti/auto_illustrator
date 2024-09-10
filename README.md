# AutoIllustrator

## About
This is a small script I used to create card images for a card game.
It's useful to get a prototype quickly in tabletop simulator (or print and cut it, if you prefer).

The cards are read from an xlsx file and used to fill in one ore more SVG templates.
It's quite flexible if you tinker a little with the script and the SVG file, I'm still using it (albeit with some
game-specific changes not included here).

I only tested it on Linux but code should be platform agnostic.


## Using
To use it just edit the .xlsx file in `sources`, the SVG templates in `templates` and provide .webp images with filenames
matching the card "Names" inside `pictures`. Then just run `uv run src/auto_illustrator.py`

BTW code is really short and easy to read. I included a very simple example in the repo that should be self-explanatory.
