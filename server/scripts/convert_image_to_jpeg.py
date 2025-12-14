#!/usr/bin/env python3
"""
Convert images in a folder to JPEG format for backend compatibility.

This script converts AVIF and other formats to JPEG, which works well with
VersatileImageField for thumbnail generation.
"""

import sys
from pathlib import Path
from PIL import Image


def convert_image_to_jpeg(input_path, output_path=None, quality=95):
    """
    Convert an image to JPEG format.

    Args:
        input_path: Path to input image file
        output_path: Path to save converted image (default: same name with .jpg extension)
        quality: JPEG quality (1-100, higher = better quality but larger file)

    Returns:
        Path to converted image, or None if conversion failed
    """
    try:
        # Open image
        image = Image.open(input_path)

        # Convert to RGB if necessary (handles RGBA, LA, P modes)
        if image.mode in ("RGBA", "LA", "P"):
            # Create white background for transparency
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            # Paste image onto white background, using alpha channel as mask
            if image.mode in ("RGBA", "LA"):
                rgb_image.paste(image, mask=image.split()[-1])
            else:
                rgb_image.paste(image)
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Determine output path
        if output_path is None:
            input_stem = Path(input_path).stem
            input_dir = Path(input_path).parent
            output_path = input_dir / f"{input_stem}.jpg"

        # Save as JPEG
        image.save(output_path, format="JPEG", quality=quality, optimize=True)

        return str(output_path)

    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return None


def convert_folder_images(
    folder_path, output_folder=None, quality=95, delete_originals=False
):
    """
    Convert all images in a folder to JPEG format.

    Args:
        folder_path: Path to folder containing images
        output_folder: Folder to save converted images (default: same folder)
        quality: JPEG quality (1-100)
        delete_originals: If True, delete original files after successful conversion
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist")
        return

    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory")
        return

    # Supported image extensions
    image_extensions = {".avif", ".png", ".webp", ".tiff", ".tif", ".bmp", ".gif"}

    # Find all image files
    image_files = []
    for ext in image_extensions:
        image_files.extend(folder.glob(f"*{ext}"))
        image_files.extend(folder.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"No images found in '{folder_path}'")
        return

    print(f"Found {len(image_files)} image(s) to convert:")
    for img in image_files:
        print(f"  - {img.name}")

    # Create output folder if specified
    if output_folder:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = folder

    converted = 0
    failed = 0

    for image_file in image_files:
        print(f"\nConverting: {image_file.name}")

        # Determine output path
        if output_folder:
            output_file = output_path / f"{image_file.stem}.jpg"
        else:
            output_file = output_path / f"{image_file.stem}.jpg"

        # Convert image
        result = convert_image_to_jpeg(image_file, output_file, quality)

        if result:
            print(f"  ✅ Saved to: {result}")

            # Delete original if requested and conversion succeeded
            if delete_originals:
                try:
                    image_file.unlink()
                    print(f"  🗑️  Deleted original: {image_file.name}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete original: {str(e)}")

            converted += 1
        else:
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Total images: {len(image_files)}")
    print(f"Successfully converted: {converted}")
    print(f"Failed: {failed}")
    print("=" * 60)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python convert_images.py <folder_path> [options]")
        print("\nOptions:")
        print("  --output <folder>    Save converted images to different folder")
        print("  --quality <1-100>    JPEG quality (default: 95)")
        print("  --delete-originals   Delete original files after conversion")
        print("\nExample:")
        print("  python convert_images.py ./images --output ./converted --quality 90")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_folder = None
    quality = 95
    delete_originals = False

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_folder = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--quality" and i + 1 < len(sys.argv):
            try:
                quality = int(sys.argv[i + 1])
                if not (1 <= quality <= 100):
                    print("Error: Quality must be between 1 and 100")
                    sys.exit(1)
            except ValueError:
                print("Error: Quality must be a number")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == "--delete-originals":
            delete_originals = True
            i += 1
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)

    convert_folder_images(folder_path, output_folder, quality, delete_originals)


if __name__ == "__main__":
    main()
