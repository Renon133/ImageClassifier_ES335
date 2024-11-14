import os
import requests
from duckduckgo_search import DDGS
from urllib.parse import urlparse, unquote
import mimetypes
import argparse

# Function to download images
def download_images(search_term, num_images, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"Created directory: {save_folder}")

    downloaded_count = 0
    attempts = 0

    with DDGS() as ddgs:
        while downloaded_count < num_images:
            for result in ddgs.images(search_term):
                if downloaded_count >= num_images:
                    break
                try:
                    image_url = result.get('image')
                    if not image_url:
                        print("No image URL found in result, skipping.")
                        continue

                    print(f"Downloading image from URL: {image_url}")
                    img_data = requests.get(image_url, timeout=10)
                    img_data.raise_for_status()

                    # Determine file extension
                    parsed_url = urlparse(image_url)
                    path = unquote(parsed_url.path)
                    file_extension = os.path.splitext(path)[-1].lower()

                    if not file_extension or len(file_extension) > 5:
                        content_type = img_data.headers.get('Content-Type')
                        file_extension = mimetypes.guess_extension(content_type)
                        if not file_extension:
                            print(f"Unable to determine file extension for {image_url}, skipping.")
                            continue

                    file_name = f"{search_term.replace(' ', '_')}_{downloaded_count + 1}{file_extension}"
                    file_path = os.path.join(save_folder, file_name)

                    # Save the image
                    with open(file_path, 'wb') as img_file:
                        img_file.write(img_data.content)

                    print(f"Saved image to: {file_path}")

                    downloaded_count += 1
                    print(f"Downloaded {downloaded_count}/{num_images} images.")

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {image_url}: {e}")
                except Exception as e:
                    print(f"Error saving image from {image_url}: {e}")

                attempts += 1
                if attempts > num_images * 3:
                    print("Maximum attempts reached, stopping download.")
                    break

    print(f"Downloaded {downloaded_count} images to {save_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images using DuckDuckGo search.")
    parser.add_argument('search_term', type=str, help='The search term to use for finding images.')
    parser.add_argument('num_images', type=int, help='The number of images to download.')
    parser.add_argument('save_folder', type=str, help='The folder where images will be saved.')

    args = parser.parse_args()

    print("Starting image download...")
    download_images(args.search_term, args.num_images, args.save_folder)
    print("Image download completed.")
