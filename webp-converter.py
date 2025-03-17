import os
import subprocess
import sys
from multiprocessing import Pool, cpu_count

out_dir = "output_files"
input_dir = "./input_files"
extensions = (".png", ".jpg", ".jpeg", ".tiff", ".webp")
script_dir = os.path.dirname(os.path.realpath(__file__))
libwebp = os.path.join(script_dir, "libwebp", "libwebp-1.5.0-windows-x64", "bin", "cwebp.exe")

def find_image_paths():
    """Finds image file paths in the input directory."""
    images = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(extensions):
                images.append(os.path.join(root, file))
    return images

def convert_image(image_path, quality):
    """Converts a single image to WebP format."""
    output_file = os.path.join(out_dir, os.path.splitext(os.path.basename(image_path))[0] + ".webp")
    try:
        result = subprocess.run(
            [libwebp, "-quiet", "-q", str(quality), image_path, "-o", output_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return (image_path, True)  # Success
    except subprocess.CalledProcessError:
        return (image_path, False)  # Failure

def convert_all(quality):
    """Parallelizes image conversion."""
    images = find_image_paths()
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with Pool(processes=cpu_count()) as pool:
        results = pool.starmap(convert_image, [(img, quality) for img in images])

    failed_images = [img for img, success in results if not success]
    
    print(f"Converted {len(images) - len(failed_images)} image(s) to WebP format.")
    
    if failed_images:
        print(f"Failed to convert {len(failed_images)} image(s):")
        for fail in failed_images:
            print(f"- {fail}")

if __name__ == "__main__":
    quality = sys.argv[1] if len(sys.argv) > 1 else "80"
    convert_all(quality)
