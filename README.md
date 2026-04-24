# matugen-palettes

Hand-crafted [Material You](https://m3.material.io/styles/color/the-color-system/key-colors-tones) palettes for [matugen](https://github.com/InioX/matugen), allowing fixed themes to be applied system-wide without needing a source wallpaper.

## Usage

Palettes are selected via the wallpaper/theme picker script (`~/.config/rofi/bin/wallpaper.sh`), which reads JSONs from `~/.config/matugen/palettes/`. After selecting a palette, matugen applies it as:

```sh
matugen json ~/.config/matugen/palettes/<theme>.json
```

The wallpaper path is then restored manually since `matugen json` doesn't know the current image.

## Installation

```sh
make install   # symlinks all JSONs to ~/.config/matugen/palettes/
make uninstall # removes those symlinks
make check     # validates all palettes (contrast ratios, missing roles, etc.)
```

> The rofi picker uses `find -L` to follow symlinks, so `make install` is all that's needed.

## Palettes

| File | Theme | Source / Key Color |
|------|-------|--------------------|
| `dracula.json` | [Dracula](https://draculatheme.com/) | `#bd93f9` (purple) |
| `catpuccin.json` | [Catppuccin Mocha](https://catppuccin.com/) | `#cba6f7` (mauve) |
| `gruvbox.json` | [Gruvbox Dark](https://github.com/morhetz/gruvbox) | `#fabd2f` (yellow) |
| `tokyonight.json` | [Tokyo Night](https://github.com/folke/tokyonight.nvim) | `#bb9af7` (purple) |
| `nord.json` | [Nord](https://www.nordtheme.com/) | `#88c0d0` (frost blue) |
| `rosepine.json` | [Rosé Pine Moon](https://rosepinetheme.com/) | `#c4a7e7` (iris) |
| `everforest.json` | [Everforest Dark Hard](https://github.com/sainnhe/everforest) | `#a7c080` (green) |
| `kanagawa.json` | [Kanagawa Wave](https://github.com/rebelot/kanagawa.nvim) | `#7e9cd8` (crystal blue) |
| `oxocarbon.json` | [Oxocarbon](https://github.com/nyoom-engineering/oxocarbon.nvim) | `#78a9ff` (IBM blue) |
| `darkforest.json` | Dark Forest (custom) | `#7cb87e` (forest green) |

## Color Roles

Each palette follows the Material You color system roles:

- **primary** — main accent (buttons, links, key UI)
- **secondary** — complementary accent
- **tertiary** — third accent for contrasting highlights
- **surface / surface_container** — background hierarchy (lowest → highest)
- **on_*** — foreground color intended to render on top of the paired surface/accent
- **error** — error states

All palettes provide `dark`, `light`, and `default` variants. `default` always mirrors `dark` since the system runs in dark mode — except `surface_bright`, which intentionally uses a slightly dimmed default value.

## Neovim mapping (base16)

The matugen neovim template (`~/.config/matugen/templates/neovim-colors.lua`) maps roles to base16 slots:

| base16 | Role | Semantic |
|--------|------|----------|
| base00 | background | editor bg |
| base01 | surface_container_lowest | gutter bg |
| base02 | surface_container_low | selection bg |
| base03 | outline_variant | invisibles |
| base04 | on_surface_variant | status bar fg |
| base05 | on_surface | default text |
| base06 | inverse_on_surface | light fg |
| base07 | surface_bright | bright highlights |
| base08 | tertiary (−5) | variables |
| base09 | tertiary | constants |
| base0A | secondary | types / warnings |
| base0B | primary | strings / success |
| base0C | on_tertiary_container | regex / escape |
| base0D | on_primary_container | functions |
| base0E | on_secondary_container | keywords |
| base0F | secondary (−10) | deprecated |

## Validation

`validate.py` checks every palette for:

- Missing required Material You roles
- `default ≠ dark` mismatches
- WCAG contrast ratios: body text (4.5:1), neovim syntax slots (3:1), comments (2:1)
- `on_X_container` being darker than `surface` (would make syntax highlights invisible)

```sh
python3 validate.py          # all palettes
python3 validate.py nord.json # single palette
make check                   # same as above via make
```

## Adding a new palette

1. Copy an existing JSON and adjust the color values to match your theme.
2. Ensure every `default` value matches `dark` (the system uses dark mode and templates reference `.default`).
3. Ensure `on_X_container` colors are the **bright** accent versions — these are used as syntax highlight foregrounds in neovim.
4. Run `make check` to validate contrast ratios before installing.
5. Run `make install` to symlink the file into `~/.config/matugen/palettes/`.
6. Set `image` to a representative wallpaper path (used by hyprpaper after applying the theme).
