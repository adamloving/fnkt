#!/usr/bin/env python3
"""
Download and resize images from a webpage.

This script downloads all images from a given webpage and resizes them to a specified size.
It is fully self-contained and will install its own dependencies when run.

Required packages (installed automatically):
    - requests>=2.31.0
    - beautifulsoup4>=4.12.0
    - Pillow>=10.0.0

Usage:
    python download_images.py --url https://example.com [--size 800 600] [--output-dir downloaded_images]

Example:
    python download_images.py --url https://example.com --size 1024 768 --output-dir my_images
"""

import os
import sys
import subprocess
import logging
import argparse
from typing import List, Tuple, Optional
from urllib.parse import urljoin
from pathlib import Path

DEPENDENCIES = {
    'requests': '2.31.0',
    'beautifulsoup4': '4.12.0',
    'Pillow': '10.0.0'
}

def setup_dependencies() -> None:
    """Install required packages if they're not already installed."""
    try:
        # Format dependencies with versions
        packages_with_versions = [f"{pkg}>={ver}" for pkg, ver in DEPENDENCIES.items()]

        # Determine if running in a virtual environment using a robust check including the VIRTUAL_ENV env var
        in_virtualenv = ('VIRTUAL_ENV' in os.environ) or (hasattr(sys, 'real_prefix') or (sys.prefix != getattr(sys, 'base_prefix', sys.prefix))) or ('venv' in sys.executable.lower())

        # Build install command conditionally
        install_cmd = [sys.executable, '-m', 'pip', 'install']
        if not in_virtualenv:
            install_cmd.append('--user')
        install_cmd.append('--quiet')
        install_cmd.extend(packages_with_versions)

        subprocess.check_call(
            install_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logging.info("Dependencies checked and installed if needed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install required packages: {e}")
        sys.exit(1)

    # Now that dependencies are installed, we can import them
    global requests, BeautifulSoup, Image
    import requests
    from bs4 import BeautifulSoup
    from PIL import Image

def get_image_urls(webpage_url: str) -> List[str]:
    """Extract all image URLs from a webpage."""
    try:
        response = requests.get(webpage_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = [urljoin(webpage_url, img.get('src'))
                for img in soup.find_all('img')
                if img.get('src')]
        logging.info(f"Found {len(urls)} image(s) on the webpage.")
        return urls
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve images from {webpage_url}: {e}")
        return []

def download_and_resize_image(url: str, output_path: str, size: Tuple[int, int]) -> None:
    """Download an image and resize it to the specified dimensions."""
    try:
        # Download
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Save original
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        
        # Resize
        with Image.open(output_path) as img:
            img = img.convert('RGB')
            img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(output_path, quality=95)
        
        logging.info(f"Successfully processed {url}")
    except Exception as e:
        logging.error(f"Failed to process {url}: {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logging.info(f"Cleaned up incomplete file: {output_path}")
            except OSError:
                pass

def resolve_output_dir(output_dir: str, artifacts: List[str]) -> str:
    """Resolve the output directory based on artifact mappings."""
    # Expand user directory if present
    output_dir = os.path.expanduser(output_dir)
    
    # Check artifact mappings
    for artifact in artifacts:
        try:
            local_path, container_path = artifact.split(':')
            # Expand user directory in local path
            local_path = os.path.expanduser(local_path)
            # If the container path matches our output dir, use the local path
            if container_path.rstrip('/') == output_dir.rstrip('/'):
                return local_path
        except ValueError:
            continue
    
    return output_dir

def main():
    parser = argparse.ArgumentParser(
        description="Download and resize images from a webpage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python download_images.py --url https://example.com --size 1024 768 --output-dir my_images"
    )
    parser.add_argument('--url', required=True, help="URL of the webpage to scrape images from")
    parser.add_argument('--size', nargs=2, type=int, default=[800, 600],
                      help="Output size as width height (default: 800 600)")
    parser.add_argument('--output-dir', default='downloaded_images',
                      help="Directory to save images (default: downloaded_images)")
    parser.add_argument('--artifacts', action='append', default=[],
                      help=argparse.SUPPRESS)  # Hide from help but still accept it
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Resolve the output directory
    output_dir = resolve_output_dir(args.output_dir, args.artifacts)
    
    # Ensure dependencies are installed
    setup_dependencies()

    # Create output directory with explicit permissions
    os.makedirs(output_dir, mode=0o755, exist_ok=True)
    
    # Get and process images
    image_urls = get_image_urls(args.url)
    if not image_urls:
        logging.warning("No images found to download.")
        return

    for idx, url in enumerate(image_urls, start=1):
        output_path = os.path.join(output_dir, f'image_{idx}.jpg')
        download_and_resize_image(url, output_path, tuple(args.size))
        # Set permissions on created files
        os.chmod(output_path, 0o644)

    logging.info("Image download and resize process completed.")

if __name__ == "__main__":
    main()