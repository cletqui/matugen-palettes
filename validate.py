#!/usr/bin/env python3
"""Validate matugen palette JSON files."""

import json
import sys
from pathlib import Path

REQUIRED_ROLES = [
    "background", "error", "error_container",
    "inverse_on_surface", "inverse_primary", "inverse_surface",
    "on_background", "on_error", "on_error_container",
    "on_primary", "on_primary_container",
    "on_primary_fixed", "on_primary_fixed_variant",
    "on_secondary", "on_secondary_container",
    "on_secondary_fixed", "on_secondary_fixed_variant",
    "on_surface", "on_surface_variant",
    "on_tertiary", "on_tertiary_container",
    "on_tertiary_fixed", "on_tertiary_fixed_variant",
    "outline", "outline_variant",
    "primary", "primary_container", "primary_fixed", "primary_fixed_dim",
    "scrim", "secondary", "secondary_container", "secondary_fixed", "secondary_fixed_dim",
    "shadow", "source_color",
    "surface", "surface_bright", "surface_container",
    "surface_container_high", "surface_container_highest",
    "surface_container_low", "surface_container_lowest",
    "surface_dim", "surface_tint", "surface_variant",
    "tertiary", "tertiary_container", "tertiary_fixed", "tertiary_fixed_dim",
]

# (foreground_role, background_role, min_ratio, description)
CONTRAST_CHECKS = [
    ("on_surface",              "surface",    4.5, "body text"),
    ("on_background",           "background", 4.5, "body text on background"),
    ("on_primary",              "primary",    4.5, "text on primary button"),
    ("on_secondary",            "secondary",  4.5, "text on secondary button"),
    ("on_tertiary",             "tertiary",   4.5, "text on tertiary button"),
    ("on_primary_container",    "surface",    3.0, "neovim base0D — functions"),
    ("on_secondary_container",  "surface",    3.0, "neovim base0E — keywords"),
    ("on_tertiary_container",   "surface",    3.0, "neovim base0C — regex/escape"),
    ("primary",                 "surface",    3.0, "neovim base0B — strings"),
    ("secondary",               "surface",    3.0, "neovim base0A — types"),
    ("tertiary",                "surface",    3.0, "neovim base08/09 — variables"),
    ("outline",                 "surface",    2.0, "neovim comments / muted text"),
]

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def hex_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    r, g, b = hex_to_linear(r), hex_to_linear(g), hex_to_linear(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def get_color(colors: dict, role: str, variant: str = "default") -> str | None:
    return colors.get(role, {}).get(variant, {}).get("color")


def validate(path: str) -> bool:
    name = Path(path).stem
    errors: list[str] = []
    warnings: list[str] = []

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"{RED}FAIL{RESET} {BOLD}{name}{RESET}: cannot parse JSON — {e}")
        return False

    colors = data.get("colors", {})

    # 1. Required roles
    for role in REQUIRED_ROLES:
        if role not in colors:
            errors.append(f"missing role: {role}")

    # 2. default must equal dark (surface_bright intentionally uses a dimmed default)
    ALLOWED_DEFAULT_MISMATCH = {"surface_bright"}
    for role, variants in colors.items():
        dark    = (variants.get("dark",    {}) or {}).get("color", "")
        default = (variants.get("default", {}) or {}).get("color", "")
        if dark and default and dark.lower() != default.lower():
            if role in ALLOWED_DEFAULT_MISMATCH:
                warnings.append(f"{role}: default ({default}) ≠ dark ({dark}) [intentional]")
            else:
                errors.append(f"{role}: default ({default}) ≠ dark ({dark})")

    # 3. Contrast checks
    for fg_role, bg_role, min_ratio, desc in CONTRAST_CHECKS:
        fg = get_color(colors, fg_role)
        bg = get_color(colors, bg_role)
        if not fg or not bg:
            continue
        try:
            ratio = contrast(fg, bg)
        except Exception:
            warnings.append(f"could not compute contrast for {fg_role} / {bg_role}")
            continue
        if ratio < min_ratio:
            msg = f"{fg_role} on {bg_role}: {ratio:.2f}:1 < {min_ratio}:1 — {desc} [{fg} on {bg}]"
            if min_ratio >= 4.5:
                errors.append(msg)
            else:
                warnings.append(msg)

    # 4. Sanity: on_X_container should not be darker than surface_container
    for hue in ("primary", "secondary", "tertiary"):
        on_c  = get_color(colors, f"on_{hue}_container")
        surf  = get_color(colors, "surface")
        if on_c and surf:
            try:
                if luminance(on_c) < luminance(surf):
                    warnings.append(
                        f"on_{hue}_container ({on_c}) is darker than surface ({surf}) "
                        f"— will be invisible as syntax highlight"
                    )
            except Exception:
                pass

    has_errors   = bool(errors)
    has_warnings = bool(warnings)
    if has_errors:
        status = f"{RED}FAIL{RESET}"
    elif has_warnings:
        status = f"{YELLOW}WARN{RESET}"
    else:
        status = f"{GREEN}OK  {RESET}"

    print(f"{status} {BOLD}{name}{RESET}")
    for e in errors:
        print(f"     {RED}✗{RESET} {e}")
    for w in warnings:
        print(f"     {YELLOW}!{RESET} {w}")

    return not has_errors


def main() -> None:
    paths = sys.argv[1:]
    if not paths:
        paths = sorted(str(p) for p in Path(".").glob("*.json"))
    if not paths:
        print("No JSON files to validate.")
        sys.exit(1)

    print(f"{DIM}Validating {len(paths)} palette(s)…{RESET}\n")
    results = [validate(p) for p in paths]
    print()
    passed = sum(results)
    total  = len(results)
    if passed == total:
        print(f"{GREEN}{BOLD}All {total} palettes passed.{RESET}")
    else:
        print(f"{RED}{BOLD}{total - passed}/{total} palette(s) failed.{RESET}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
