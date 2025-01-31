#!/usr/bin/env python3
"""download all images from a webpage and resize them to 800x600"""

# fnkt run workflows/workflow_f75be458.py --url "https://example.com"

import os
import sys
import subprocess
import logging

def setup_dependencies():
    required_packages = ['requests', 'beautifulsoup4', 'Pillow']
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                __import__('bs4')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    if missing_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_packages])
            logging.info(f"Installed missing packages: {', '.join(missing_packages)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install packages {missing_packages}: {e}")
            sys.exit(1)

def init_artifacts():
    try:
        os.makedirs('downloaded_images', exist_ok=True)
        logging.info("Initialized artifacts directory.")
    except Exception as e:
        logging.error(f"Failed to initialize artifacts: {e}")
        sys.exit(1)

def download_image(url, path):
    import requests
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logging.info(f"Downloaded image from {url} to {path}.")
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")

def resize_image(path, size=(800, 600)):
    from PIL import Image
    try:
        with Image.open(path) as img:
            img = img.convert('RGB')
            img = img.resize(size, Image.ANTIALIAS)
            img.save(path)
        logging.info(f"Resized image {path} to {size}.")
    except Exception as e:
        logging.error(f"Failed to resize {path}: {e}")

def get_image_urls(webpage_url):
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    try:
        response = requests.get(webpage_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        urls = []
        for img in img_tags:
            src = img.get('src')
            if src:
                full_url = urljoin(webpage_url, src)
                urls.append(full_url)
        logging.info(f"Found {len(urls)} image(s) on the webpage.")
        return urls
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve images from {webpage_url}: {e}")
        return []

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    setup_dependencies()
    init_artifacts()
    try:
        if len(sys.argv) < 2:
            logging.error("Please provide a webpage URL as an argument")
            sys.exit(1)
        webpage_url = sys.argv[1].strip()
        if not webpage_url:
            logging.error("No URL provided. Exiting.")
            sys.exit(1)
        image_urls = get_image_urls(webpage_url)
        if not image_urls:
            logging.info("No images found to download.")
            return
        for idx, url in enumerate(image_urls, start=1):
            try:
                filename = os.path.join('downloaded_images', f'image_{idx}.jpg')
                download_image(url, filename)
                resize_image(filename)
            except Exception as e:
                logging.error(f"Error processing image {url}: {e}")
        logging.info("Image download and resize process completed.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()