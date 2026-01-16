#!/usr/bin/env python3
"""
Generate NFO-style SVG files for GitHub profile README.
Creates dark_mode.svg and light_mode.svg with embedded stats.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Import stats functions from preview
from preview import get_claude_stats, get_github_stats, format_number


def escape_xml(s):
    """Escape XML special characters."""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def generate_svg(mode="dark"):
    """Generate SVG content for the given color mode."""

    # Get stats
    claude = get_claude_stats()
    github = get_github_stats()

    # Color schemes
    if mode == "dark":
        colors = {
            'bg': '#0d1117',
            'text': '#39c5cf',
            'gray': '#6e7681',
            'magenta': '#bc8cff',
            'green': '#3fb950',
            'yellow': '#d29922',
        }
    else:
        colors = {
            'bg': '#ffffff',
            'text': '#0969da',
            'gray': '#656d76',
            'magenta': '#8250df',
            'green': '#1a7f37',
            'yellow': '#9a6700',
        }

    c = colors
    width = 800
    font_size = 14
    line_height_tight = 13  # For ASCII art blocks (slightly overlap to eliminate gaps)
    line_height_normal = 20  # For stat lines (readable spacing)
    y_start = 30
    content_width = 90  # chars for stat lines

    # Stats formatter with dots (right-aligned values)
    def stat_line(key, value):
        key_str = f"{key}:"
        val_str = str(value)
        dots = '.' * (content_width - len(key_str) - len(val_str) - 2)
        return f"{key_str} {dots} {val_str}"

    # Build content lines with spacing type
    # Each entry: (line_text, color, spacing_type)
    # spacing_type: "tight" for ASCII art, "normal" for stats, "blank" for empty
    lines = []

    # Header art - gradient smiley face (90 chars wide)
    header_art = [
        "                                       ▒▓▓█████▓▓▓░                                       ",
        "                                ▓█████████▓▓▓▓▓██████████▓                                ",
        "                           ▓██████░░░░░░░░░░░░░░░░░░░░░░██████▒                           ",
        "                        ▓████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒████▓                        ",
        "                     ▓████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████▓                     ",
        "                   ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████                   ",
        "                 ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████                 ",
        "               ▒███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███▒               ",
        "              ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███              ",
        "            ░██▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓██░            ",
        "           ▓██▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██▓           ",
        "          ▓██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██▓          ",
        "         ▓██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██▓         ",
        "        ▒██░░░░░░░░░░░░░░░░░░░░████▓░░░░░░░░░░░░░░░░░░▓████░░░░░░░░░░░░░░░░░░░░██▓        ",
        "        ██▓░░░░░░░░░░░░░░░░░░░███████░░░░░░░░░░░░░░░░███████░░░░░░░░░░░░░░░░░░░▒██        ",
        "       ███░░░░░░░░░░░░░░░░░░░████████░░░░░░░░░░░░░░░░████████░░░░░░░░░░░░░░░░░░░███       ",
        "       ██▒░░░░░░░░░░░░░░░░░░░░███████░░░░░░░░░░░░░░░░███████░░░░░░░░░░░░░░░░░░░░░██       ",
        "      ███░░░░░░░░░░░░░░░░░░░░░██████░░░░░░░░░░░░░░░░░░█████░░░░░░░░░░░░░░░░░░░░░░███      ",
        "      ███░░░░░░░░░░░░░░░░░░░░░░░░▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███      ",
        "      ██▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒██      ",
        "      ██▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██      ",
        "      ██▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██      ",
        "      ██▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒██      ",
        "      ███░░░░░░░░░░░░░░▒█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█████▒░░░░░░░░░░░░░░▓██      ",
        "      ███░░░░░░░░░░░░░█████▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒█████░░░░░░░░░░░░░███      ",
        "       ██░░░░░░░░░░░░░▓█░███▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒███▒█▓░░░░░░░░░░░░░██░      ",
        "       ███░░░░░░░░░░░░░░░░▓███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███▓░░░░░░░░░░░░░░░░███       ",
        "        ██▒░░░░░░░░░░░░░░░░░████░░░░░░░░░░░░░░░░░░░░░░░░░░████░░░░░░░░░░░░░░░░░░██▒       ",
        "        ▓██░░░░░░░░░░░░░░░░░░▒█████▒░░░░░░░░░░░░░░░░░░▒█████▒░░░░░░░░░░░░░░░░░░███        ",
        "         ███░░░░░░░░░░░░░░░░░░░▓████████░░░░░░░░░░████████▒░░░░░░░░░░░░░░░░░░░███         ",
        "          ███░░░░░░░░░░░░░░░░░░░░░▒████████████████████░░░░░░░░░░░░░░░░░░░░░░███          ",
        "           ███░░░░░░░░░░░░░░░░░░░░░░░░░▓▓████████▓▓░░░░░░░░░░░░░░░░░░░░░░░░░███           ",
        "            ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███            ",
        "             ███▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒███             ",
        "               ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███░              ",
        "                ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████                ",
        "                  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████                  ",
        "                    ████▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████                    ",
        "                      ▓████▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒████▓                      ",
        "                         ▓█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░█████▓                         ",
        "                            ░████████░░░░░░░░░░░░░░░▒████████▒                            ",
        "                                 ░██████████████████████░                                 ",
    ]
    for art in header_art:
        lines.append((art, "yellow", "tight"))

    lines.append(("", "text", "blank"))
    lines.append(("", "text", "blank"))
    lines.append(("ai developer  ·  prompt whisperer  ·  token burner", "gray", "normal"))
    lines.append(("", "text", "blank"))
    lines.append(("", "text", "blank"))

    # System info warez header - orange for variety
    # S    Y    S    T    E    M       I  N    F    O
    for hdr in [
        "▄▀▀  ▀▄ ▄▀ ▄▀▀  ▀▀▀█ ▄▀▀  ▄▀▄▀▄   ▀ ▄▀▀▄ ▄▀▀  ▄▀▀▄",
        "▀▀█   ▀█   ▀▀█   ▀▀  ▓▀   █ ▀ █   █ █  █ ▓▀   █  █",
        "▀▀▀   ▀    ▀▀▀   ▀   ▀▀▀  ▀   ▀   ▀ ▀  ▀ ▀    ▀▀▀ ",
    ]:
        lines.append((hdr, "orange", "tight"))

    lines.append(("", "text", "blank"))

    for key, val in [
        ("Location", "NYC, NY"),
        ("Shell", "living tissue over metal endoskeleton"),
        ("Languages", "english, bad english, help files"),
        ("Focus", "AI/ML, Developer Tools, waning"),
    ]:
        lines.append((stat_line(key, val), "gray", "normal"))

    lines.append(("", "text", "blank"))
    lines.append(("", "text", "blank"))

    # Claude Code warez header - tight spacing
    for hdr in [
        "▄▀▀  ▓   ▄▀▀▄ ▓  ▄ ▄▀▀▄ ▄▀▀    ▄▀▀  ▄▀▀▄ ▄▀▀▄ ▄▀▀ ",
        "█    █   █▀▀▓ █  ▓ █  ▓ ▓▀     █    █  ▓ █  ▓ ▓▀  ",
        " ▀▀  ▀▀▀ ▀    ▀▀▀▀ ▀▀▀▀ ▀▀▀     ▀▀   ▀▀  ▀▀▀▀ ▀▀▀ ",
    ]:
        lines.append((hdr, "magenta", "tight"))

    lines.append(("", "text", "blank"))

    for key, val in [
        ("Sessions", format_number(claude['sessions'])),
        ("Messages", format_number(claude['messages'])),
        ("Total Tokens", format_number(claude['total_tokens'])),
        ("Est. API Cost Saved", f"${claude['cost_estimate']:,.0f}"),
    ]:
        lines.append((stat_line(key, val), "gray", "normal"))

    lines.append(("", "text", "blank"))
    lines.append(("", "text", "blank"))

    # GitHub stats warez header - tight spacing
    for hdr in [
        "▄▀▀  ▀ ▀▀▀█ ▓  ▄ ▓  ▄ ▄▀▄   ▄▀▀  ▀▀▀█ ▄▀▀▄ ▀▀▀█ ▄▀▀ ",
        "█ ▀▓ █  ▀▀  █▀▀▓ █  ▓ █▀▀▄  ▀▀█   ▀▀  █▀▀▓  ▀▀  ▀▀█ ",
        " ▀▀  ▀  ▀   ▀  ▀ ▀▀▀▀ ▀▀▀   ▀▀▀   ▀   ▀  ▀  ▀   ▀▀▀ ",
    ]:
        lines.append((hdr, "green", "tight"))

    lines.append(("", "text", "blank"))

    for key, val in [
        ("Repositories", github.get('repos', 0)),
        ("Contributed To", github.get('contributed_repos', 0)),
        ("Total Commits", github.get('commits', 0)),
        ("Pull Requests", github.get('prs', 0)),
    ]:
        lines.append((stat_line(key, val), "gray", "normal"))

    # LOC line - special formatting with dots
    loc_total = github.get('loc_total', 0)
    loc_added = github.get('loc_added', 0)
    loc_deleted = github.get('loc_deleted', 0)
    loc_value = f"{loc_total:,} ( +{loc_added:,}, -{loc_deleted:,} )"
    lines.append((f"__LOC__{loc_value}__", "loc", "normal"))

    lines.append(("", "text", "blank"))

    # Footer
    lines.append(("// TODO: write great footer", "gray", "normal"))
    lines.append(("", "text", "blank"))
    lines.append((f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}", "gray", "normal"))

    # Calculate height based on variable line heights
    total_height = y_start
    for _, _, spacing in lines:
        if spacing == "tight":
            total_height += line_height_tight
        elif spacing == "blank":
            total_height += line_height_normal // 2  # Half height for blanks
        else:
            total_height += line_height_normal
    height = total_height + 30

    # Build SVG
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
@font-face {{
    src: local('Consolas'), local('Monaco'), local('Menlo');
    font-family: 'MonoFallback';
    font-display: swap;
}}
text {{
    font-family: 'MonoFallback', ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
    font-size: {font_size}px;
    white-space: pre;
    dominant-baseline: text-before-edge;
}}
.text {{ fill: {c['text']}; }}
.gray {{ fill: {c['gray']}; }}
.magenta {{ fill: {c['magenta']}; }}
.green {{ fill: {c['green']}; }}
.red {{ fill: #f85149; }}
.orange {{ fill: #f0883e; }}
.yellow {{ fill: {c['yellow']}; }}
</style>
<rect width="{width}" height="{height}" fill="{c['bg']}" rx="10"/>
'''

    # Add centered lines with variable spacing
    y = y_start
    for line, color, spacing in lines:
        # Special handling for LOC line with colored +/-
        if line.startswith('__LOC__'):
            # Extract the value part
            loc_value = line.replace('__LOC__', '').replace('__', '')
            # Build dotted line: Lines of Code: ........ value
            key_str = "Lines of Code:"
            dots_len = content_width - len(key_str) - len(loc_value) - 2
            dots = '.' * max(dots_len, 3)

            # Parse out the +number and -number for coloring
            match = re.search(r'([\d,]+) \( \+([\d,]+), -([\d,]+) \)', loc_value)
            if match:
                total, added, deleted = match.groups()
                svg += f'<text x="{width // 2}" y="{y}" text-anchor="middle">'
                svg += f'<tspan class="gray">{key_str} {dots} {total} ( </tspan>'
                svg += f'<tspan class="green">+{added}</tspan>'
                svg += f'<tspan class="gray">, </tspan>'
                svg += f'<tspan class="red">-{deleted}</tspan>'
                svg += f'<tspan class="gray"> )</tspan>'
                svg += '</text>\n'
            else:
                svg += f'<text x="{width // 2}" y="{y}" text-anchor="middle" class="gray">{key_str} {dots} {loc_value}</text>\n'
        elif line:  # Non-empty line
            escaped = escape_xml(line)
            svg += f'<text x="{width // 2}" y="{y}" text-anchor="middle" class="{color}">{escaped}</text>\n'
        # else: blank line, just advance y

        # Advance y based on spacing type
        if spacing == "tight":
            y += line_height_tight
        elif spacing == "blank":
            y += line_height_normal // 2
        else:
            y += line_height_normal

    svg += '</svg>'
    return svg


def main():
    """Generate both dark and light mode SVGs."""
    script_dir = Path(__file__).parent

    # Generate dark mode
    dark_svg = generate_svg("dark")
    dark_path = script_dir / "dark_mode.svg"
    with open(dark_path, 'w', encoding='utf-8') as f:
        f.write(dark_svg)
    print(f"Generated: {dark_path}")

    # Generate light mode
    light_svg = generate_svg("light")
    light_path = script_dir / "light_mode.svg"
    with open(light_path, 'w', encoding='utf-8') as f:
        f.write(light_svg)
    print(f"Generated: {light_path}")


if __name__ == "__main__":
    main()
