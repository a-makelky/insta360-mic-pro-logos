# Contributing

Thanks for helping improve the Insta360 Mic Pro logo kit.

The goal is simple: logos should be easy to find, easy to download, and ready to load into the Insta360 app without extra editing.

## Request A Logo

Open a logo request issue and include:

- Brand or product name
- Official website
- Best source link for the logo, if you have one
- Whether you want color, high contrast, or both

## Add A Logo

Add one folder under `logos/<brand-slug>/`.

Expected structure:

```text
logos/example/
  README.md
  color/
    example-symbol-color-micpro-240x208-transparent.png
  mono/
    example-symbol-micpro-240x208-transparent.png
```

Each PNG must be:

- 240 x 208 px
- PNG
- Transparent background
- Readable at small size

Then update:

- `catalog.json`
- `site/logos.json`

Run validation before opening a pull request:

```text
python3 tools/validate_assets.py
```

## Quality Bar

Think of the Mic Pro screen like a helmet sticker, not a poster. Simple marks usually work better than full wordmarks. A logo can be accurate and still be a bad fit for this screen if the details are too tiny.

## Source And Trademark Rules

- Prefer official brand assets or widely cited public logo sources.
- Include the source URL in `catalog.json` and the logo folder README.
- Do not claim ownership of a third-party mark.
- Do not imply a brand or Insta360 endorses this project.
