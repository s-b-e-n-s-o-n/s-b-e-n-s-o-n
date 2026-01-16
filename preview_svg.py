#!/usr/bin/env python3
"""
Preview SVG files locally using system browser or Quick Look.
"""

import subprocess
import sys
from pathlib import Path


def preview_svg(svg_path: str, method: str = "browser"):
    """Preview an SVG file using the specified method."""
    path = Path(svg_path)
    if not path.exists():
        print(f"Error: {svg_path} not found")
        return False

    if method == "browser":
        # Open in default browser
        subprocess.run(["open", str(path)])
    elif method == "quicklook":
        # macOS Quick Look
        subprocess.run(["qlmanage", "-p", str(path)])
    else:
        print(f"Unknown method: {method}")
        return False

    return True


def main():
    script_dir = Path(__file__).parent

    # Default to dark mode SVG
    svg_file = "dark_mode.svg"
    method = "browser"

    # Parse args
    for arg in sys.argv[1:]:
        if arg in ("light", "light_mode", "light_mode.svg"):
            svg_file = "light_mode.svg"
        elif arg in ("dark", "dark_mode", "dark_mode.svg"):
            svg_file = "dark_mode.svg"
        elif arg in ("ql", "quicklook"):
            method = "quicklook"
        elif arg in ("browser", "open"):
            method = "browser"
        elif arg == "both":
            # Preview both
            preview_svg(script_dir / "dark_mode.svg", method)
            preview_svg(script_dir / "light_mode.svg", method)
            return

    preview_svg(script_dir / svg_file, method)


if __name__ == "__main__":
    main()
