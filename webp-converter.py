import shutil
import subprocess
import argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_conversion.log"),
        logging.StreamHandler()
    ]
)

extensions = (".png", ".jpg", ".jpeg", ".tiff", ".webp") # Add in additional extensions here if needed
script_dir = Path(__file__).resolve().parent
libwebp = script_dir / "libwebp" / "libwebp-1.5.0-windows-x64" / "bin" / "cwebp.exe"


def find_image_paths(input_folder):
    return [file for file in input_folder.rglob("*") if file.suffix.lower() in extensions]


# Convert single image
def convert_image(image_path, image_quality, output_folder):
    output_file = output_folder / image_path.with_suffix(".webp").name

    # If the file is already a .webp, just copy it
    if image_path.suffix.lower() == ".webp":
        shutil.copy(image_path, output_file)
        logging.info(f"{image_path.name}: Already WebP. Copied to output directory.")
        return (image_path, True) # Success tuple for copy operation
    
    try:
        result = subprocess.run(
            [libwebp, "-quiet", "-q", str(image_quality), image_path, "-o", output_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        logging.info(f"{image_path.name}: Converted to WebP")
        return (image_path, True) # Success tuple
    except subprocess.CalledProcessError as e:
        logging.error(f"Conversion failed for {image_path.name}: {e}")
        return (image_path, False) # Failure tuple


def convert_all(input_folder, image_quality):
    images = find_image_paths(input_folder)
    
    output_folder = input_folder.parent / f"{input_folder.name}_webp"
    output_folder.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting conversion of {len(images)} images.")

    with Pool(processes=cpu_count()) as pool:
        results = pool.starmap(convert_image, [(img, image_quality, output_folder) for img in images])

    failed_images = [img for img, success in results if not success]

    logging.info(f"Converted {len(images) - len(failed_images)} image(s) to WebP format.")
    
    if failed_images:
        logging.error(f"Failed to convert {len(failed_images)} image(s):")
        for fail in failed_images:
            logging.error(f"- {fail}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert all images in a folder to WebP.")
    parser.add_argument("input_folder", type=Path, help="Path to the input folder containing the files.")
    parser.add_argument("--image-quality", type=int, help="Image compression quality percentage.", default=80)
    
    args = parser.parse_args()
    convert_all(args.input_folder, args.image_quality)