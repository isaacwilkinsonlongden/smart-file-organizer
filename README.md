# Smart File Organizer

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Tests](https://img.shields.io/badge/tests-48%20passing-brightgreen)
![CLI Tool](https://img.shields.io/badge/type-CLI%20tool-purple)
![License](https://img.shields.io/badge/license-MIT-green)

A command-line tool that automatically organizes files into categorized folders based on file extensions.

Smart File Organizer scans a directory and moves files into folders such as **Images**, **Documents**, **Videos**, and more. It supports recursive scanning, customizable file mappings, collision handling, and a user-editable configuration file.

---

## Features

- Organize files by extension into categorized folders
- Recursive directory scanning
- Custom output directory support
- User-configurable extension mappings
- Dry-run mode to preview changes
- Collision handling (rename, skip, fail)
- TOML configuration file
- Fully tested with 48 unit tests

---

# Installation

There are two ways to install the tool.

---

## Option 1 — Install from GitHub (recommended for users)

Install directly from the GitHub repository:

```bash
pip install git+https://github.com/isaacwilkinsonlongden/smart-file-organizer
```

After installation, the CLI command becomes available:

```bash
organize -h
```

---

## Option 2 — Clone the repository (recommended for development)

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/isaacwilkinsonlongden/smart-file-organizer
cd smart-file-organizer

python3 -m venv venv
source venv/bin/activate

pip install -e .
```

Editable installs allow changes to the source code to immediately affect the installed tool.

---

## Basic Usage

Organize files in a directory:

```bash
organize run ~/Downloads
```

Preview changes without moving files:

```bash
organize run ~/Downloads --dry-run
```

Recursively organize files in subdirectories:

```bash
organize run ~/Downloads --recursive
```

Move organized files to a different directory:

```bash
organize run ~/Downloads --output ~/Organized
```

Example result:

```
Downloads/
    photo.jpg
    report.pdf
    video.mp4
```

After running the organizer:

```
Organized/
    Images/photo.jpg
    Documents/report.pdf
    Videos/video.mp4
```

Example console output:

```
Scanned 3 files
Found 3 files to move
Skipped 0 files

Executing moves:

Documents (1)
   Downloads/report.pdf -> Organized/Documents/report.pdf

Images (1)
   Downloads/photo.jpg -> Organized/Images/photo.jpg

Videos (1)
   Downloads/video.mp4 -> Organized/Videos/video.mp4

Execution complete. Moved 3, skipped 0
```

---

## Configuration

The tool supports a user configuration file that allows customization of file extension mappings.

By default, the configuration merges custom extension mappings with the built-in default mappings. This behavior can be disabled for complete customization.

### Initialize a configuration file

```bash
organize config init
```

### Show the current configuration

```bash
organize config show
```

### Add or update an extension mapping

Example: send `.mp3` files to a `Music` folder.

```bash
organize config set .mp3 Music
```

### Remove an extension mapping

```bash
organize config unset .mp3
```

---

## Disable Default Extension Mappings

To disable merging with the default extension mappings, you can either edit the TOML file directly or reset the configuration using the CLI.

```bash
organize config reset --blank
```

This command removes all custom mappings and sets:

```
merge_default_categories = false
use_fallback_category = false
```

---

## Reset Configuration

Restore the default configuration:

```bash
organize config reset --default
```

---

## Example Configuration File

The configuration file is stored in:

```
~/.config/smart-file-organizer/config.toml
```

Example configuration:

```toml
[general]
merge_default_categories = false
use_fallback_category = true
fallback_category = "Other"

[extensions]
".mp3" = "Music"
".log" = "Logs"
```

---

## Collision Handling

When a file already exists at the destination, the tool supports three behaviors:

| Option | Behavior |
|------|------|
| `rename` | Rename the new file (`file (1).txt`) |
| `skip` | Skip the file |
| `fail` | Stop execution with an error |

Example:

```bash
organize run ~/Downloads --collision skip
```

If no `--collision` or `-c` flag is provided, the default behavior is **rename**.

---

## Recursive Mode

Recursive mode scans subdirectories and organizes files found within them.

```bash
organize run ~/Downloads --recursive
```

Files already inside active category folders are skipped to avoid reorganizing already-sorted files.

---

## Command Help

Use the `--help` or `-h` flag to display detailed usage information for any command.

Example:

```bash
organize -h
organize run -h
organize config -h
organize config reset -h
organize config set -h
```

---

## Project Structure

```
src/organizer/
    cli.py
    config.py
    categorizer.py
    filesystem.py
    organizer.py
    executor.py

tests/
    test_cli.py
    test_config.py
    test_executor.py
    test_filesystem.py
    test_organizer.py
```

The project follows a modular structure:

- **cli.py** – command-line interface
- **config.py** – configuration handling
- **categorizer.py** – file extension categorization
- **filesystem.py** – file discovery
- **organizer.py** – planning file moves
- **executor.py** – executing file operations

---

## Running Tests

The project includes **48 unit tests** covering the CLI, planner logic, configuration handling, and execution behavior.

Run tests with:

```bash
pytest
```

---

## Example Workflow

Initialize configuration:

```bash
organize config init
```

Create a blank configuration:

```bash
organize config reset --blank
```

Set custom extension mappings:

```bash
organize config set .mp3 Music
organize config set .txt Documents
organize config set .jpg Images
organize config set .png Images
```

Preview organization:

```bash
organize run ~/Downloads -o ~/ -r -d
```

Flags:

```
-o  → --output
-r  → --recursive
-d  → --dry-run
```

Example console output:

```
Scanned 5 files
Found 4 files to move
Skipped 1 files

Dry run (no changes made)

Documents (1)
   Downloads/notes.txt -> home/Documents/notes.txt

Images (2)
   Downloads/photo.jpg -> home/Images/photo.jpg
   Downloads/wallpaper.png -> home/Images/wallpaper.png

Music (1)
   Downloads/song.mp3 -> home/Music/song.mp3

Skipped:
   Downloads/.hiddenfile
```

Run the actual organization:

```bash
organize run -r ~/Downloads -o ~/
```

Example output:

```
Scanned 5 files
Found 4 files to move
Skipped 1 files

Executing moves:

Documents (1)
   Downloads/notes.txt -> home/Documents/notes.txt

Images (2)
   Downloads/photo.jpg -> home/Images/photo.jpg
   Downloads/wallpaper.png -> home/Images/wallpaper.png

Music (1)
   Downloads/song.mp3 -> home/Music/song.mp3

Execution complete. Moved 4, skipped 1
```

---

## License

MIT License

---

## Author

Isaac Wilkinson-Longden