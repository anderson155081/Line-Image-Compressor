#!/usr/bin/env python3
"""
compress_heavy_images_fancy.py
──────────────────────────────
• Recursively scans *.jpg / *.jpeg / *.png inside a folder
• Any file > 20 MB is re‑saved just small enough to fit (default target = 19 MB)
• Keeps pixel resolution, bakes EXIF orientation into pixels
• Shows a Rich progress bar and colourised status lines

Usage
-----
python -m pip install pillow rich
python compress_heavy_images_fancy.py /path/to/folder \
       --target-mb 19 --min-quality 85 --overwrite
"""

import argparse, io, sys
from pathlib import Path
from PIL import Image, ImageOps
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn
from rich.text import Text

console = Console()

# ─────────────────────── utility helpers ────────────────────────────
def file_size_mb(p: Path) -> float:
    return p.stat().st_size / (1024 * 1024)

def strip_orientation(exif):
    """Set EXIF Orientation = 1 (normal) so pixels are already upright."""
    ORIENT = 0x0112
    if ORIENT in exif:
        exif[ORIENT] = 1
    return exif.tobytes()

def colour_status(label: str, mb: float) -> Text:
    """Pretty coloured status text."""
    if "✓" in label:
        colour = "green"
    elif "skip" in label:
        colour = "grey50"
    elif "✗" in label or "error" in label:
        colour = "red"
    else:
        colour = "yellow"
    t = Text(label.ljust(38), style=colour)
    t.append(f"{mb:6.2f} MB", style="bold")
    return t

# ───────────── compression primitives (unchanged) ───────────────────
def compress_jpeg(img, out_path, target_mb, min_q, max_q):
    lo, hi = min_q, max_q
    best_bytes = best_q = None
    while lo <= hi:
        q = (lo + hi) // 2
        buf = io.BytesIO()
        exif_bytes = strip_orientation(img.getexif())
        img.save(buf, format="JPEG", quality=q, optimize=True,
                 exif=exif_bytes, icc_profile=img.info.get("icc_profile"))
        size_mb = len(buf.getvalue()) / (1024 * 1024)
        if size_mb <= target_mb:
            best_bytes, best_q = buf.getvalue(), q
            lo = q + 1       # try higher quality
        else:
            hi = q - 1
    if best_bytes is None:
        return False, None, None
    out_path.write_bytes(best_bytes)
    return True, best_q, file_size_mb(out_path)

def compress_png(img, out_path, target_mb):
    img.save(out_path, format="PNG", optimize=True, compress_level=9)
    new_mb = file_size_mb(out_path)
    return new_mb <= target_mb, new_mb

# ───────────────────────── core routine ──────────────────────────────
def process_one(path: Path, args):
    """Handle a single image; return (label, size_MB)."""
    orig_mb = file_size_mb(path)
    if orig_mb <= 19:
        return "skip (≤19 MB)", orig_mb

    try:
        with Image.open(path) as img:
            fmt = img.format              # ← cache BEFORE transpose
            img = ImageOps.exif_transpose(img)   # bake orientation
            img.format = fmt              # (optional) restore for clarity

            out = path if args.overwrite else path.with_stem(path.stem + "_compressed")

            if fmt == "JPEG":
                ok, q, new_mb = compress_jpeg(img, out, args.target_mb,
                                              args.min_quality, 100)
                label = f"JPEG ✓ (q={q})" if ok else \
                        f"JPEG ✗ (≥q{args.min_quality} still big)"
                return label, new_mb or orig_mb

            elif fmt == "PNG":
                ok, new_mb = compress_png(img, out, args.target_mb)
                label = "PNG ✓" if ok else "PNG ✗ (still big)"
                return label, new_mb

            else:
                return f"{fmt} unsupported", orig_mb

    except Exception as e:
        return f"error: {e}", orig_mb

# ────────────────────────── CLI entry ────────────────────────────────
def cli():
    ap = argparse.ArgumentParser(
        description="Compress large images with colours and progress bar.")
    ap.add_argument("folder", help="Folder to scan")
    ap.add_argument("--target-mb", type=float, default=19.0,
                    help="Size goal after compression (MB, default 19)")
    ap.add_argument("--min-quality", type=int, default=85,
                    help="Lowest JPEG quality allowed (default 85)")
    ap.add_argument("--overwrite", action="store_true",
                    help="Replace originals instead of *_compressed copies")
    args = ap.parse_args()

    root = Path(args.folder)
    if not root.is_dir():
        console.print(f"[bold red]Folder not found:[/] {root}")
        sys.exit(1)

    files = [p for p in root.rglob("*")
             if p.suffix.lower() in {".jpg", ".jpeg", ".png"} and p.is_file()]

    console.print(f"\n[bold cyan]Scanning[/] {root} "
                  f"([bright_magenta]{len(files)}[/] images)\n")

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task("[cyan]Compressing", total=len(files))
        for p in files:
            label, size_mb = process_one(p, args)
            console.print(p.relative_to(root), "→", colour_status(label, size_mb))
            progress.advance(task)

    console.print("\n[bold green]:sparkles: All done![/]")

if __name__ == "__main__":
    cli()
