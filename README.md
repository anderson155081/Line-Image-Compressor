# 📷 compress-heavy-images-fancy

*A Python CLI tool that shrinks huge JPEG/PNG files just enough to sneak under size limits—without changing their resolution—while giving you a slick, colour‑rich progress bar.*

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-blue">
  <img alt="License" src="https://img.shields.io/github/license/your-username/compress-heavy-images-fancy">  
  <img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen">
</p>

> **Perfect for:** LINE, Slack, email, or any service that rejects images > 20 MB but you don’t want to down‑rez your gorgeous photos.

---

## ✨ Features

| Feature                        | Description                                                                                                     |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| **Auto‑target file size**      | Finds the *highest* JPEG quality that lands below your goal (default 19 MB).                                    |
| **Lossless PNG compression**   | Re‑saves PNGs with `optimize=True`, `compress_level=9`.                                                         |
| **Rotation‑safe**              | Reads the EXIF Orientation tag and *bakes* it into the pixels—no more sideways uploads.                         |
| **Rich UI**                    | Colourised status lines + live progress bar (thanks to the [Rich](https://github.com/Textualize/rich) library). |
| **Non‑destructive by default** | Adds a `_compressed` suffix so originals stay intact (`--overwrite` to replace).                                |
| **CLI‑first**                  | One‑liner usage; works recursively through sub‑folders.                                                         |

---

## 🚀 Quick Start

```bash
# 1  Install dependencies
python -m pip install pillow rich

# 2  Run on a folder of images
python compress_heavy_images_fancy.py /path/to/folder
```

Typical output:

```
Scanning /Users/me/Photos (132 images)

 DSCF2791.JPG → JPEG ✓ (q=92)                 18.97 MB
 DSCF2722.JPG → JPEG ✓ (q=94)                 18.65 MB
 DSCF2723.JPG → JPEG ✓ (q=93)                 18.88 MB
 …

████████████████████████████████████ 100% 0:12 • Done!
```

---

## 🔧 Command‑line Options

| Flag            | Default    | Purpose                                                                                        |
| --------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| `--target-mb`   | `19`       | Post‑compression size ceiling (MB). Aim a tad under the real limit (e.g. 19 for LINE’s 20 MB). |
| `--min-quality` | `85`       | Lowest JPEG quality allowed; raise to keep more detail.                                        |
| `--overwrite`   | *(absent)* | Replace original files instead of writing `*_compressed`.                                      |

Example—be *super* strict on quality, overwrite originals, and give extra head‑room:

```bash
python compress_heavy_images_fancy.py ~/Photos/RawScans \
       --target-mb 18.5 --min-quality 92 --overwrite
```

---

## 🛠️  How It Works

1. **Scan** – Walks the directory tree with `pathlib.Path.rglob`.
2. **Skip small files** – Anything ≤ 20 MB is ignored.
3. **Fix orientation** – `ImageOps.exif_transpose()` rotates/flips pixels & resets EXIF Orientation=1.
4. **JPEG** – Binary‑searches quality 100→`min-quality`, keeping the *highest* value that fits your target.
5. **PNG** – Saves once with maximum z‑lib compression. (Lossless; if still > target, the script flags it.)
6. **Output** – Writes to `<name>_compressed.<ext>` or overwrites in‑place.

The logic lives in under 200 lines of readable, dependency‑light code.

---

## 🤔 FAQ

### Will this ruin my image quality?

JPEG compression is **adaptive**—the script picks the *highest* quality that hits your target, often ≥ 92. Most users cannot see any difference in side‑by‑side blind tests.

### Why aim for 19 MB when the limit is 20 MB?

Some services add metadata or re‑encode uploads. A 19 MB buffer avoids “file too big” edge cases.

### Can it handle RAW/HEIC/GIF/WebP?

Not yet. PRs welcome!

---

## 📈 Roadmap

* [ ] Optional WebP output for even better compression.
* [ ] GUI drop‑folder (Tkinter / PySide).
* [ ] Windows & macOS context‑menu installers.

---

## 🤝 Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feat/AmazingThing`).
3. Commit your changes (`git commit -m 'feat: add AmazingThing'`).
4. Push to the branch (`git push origin feat/AmazingThing`).
5. Open a Pull Request ✨.

Please run `ruff` or `flake8` before submitting.

---

## 📜 License

This project is licensed under the **MIT License**—see `LICENSE` for details.

---

## 👤 Author

**[Anderson Chen](https://github.com/anderson155081)**
If you find this helpful, give the repo a ⭐ and feel free to reach out!

---

<p align="center"><i>Happy compressing & enjoy your perfectly oriented, size‑friendly images! 📸✨</i></p>

