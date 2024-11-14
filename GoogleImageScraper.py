import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import time
import argparse

# Function to download images from Google Images
def download_images(search_term, num_images, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"Created directory: {save_folder}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chromedriver_autoinstaller.install()  # Install ChromeDriver if not available
    driver = webdriver.Chrome(options=options)

    search_url = f"https://www.google.com/search?q={search_term}&source=lnms&tbm=isch"
    driver.get(search_url)

    time.sleep(2)  # Allow time for the page to load

    image_urls = set()
    downloaded_count = 0

    while downloaded_count < num_images:
        thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
        for thumbnail in thumbnails:
            try:
                thumbnail.click()
                time.sleep(1)
                images = driver.find_elements(By.CSS_SELECTOR, "img.n3VNCb")
                for image in images:
                    src = image.get_attribute('src')
                    if src and 'http' in src and src not in image_urls:
                        image_urls.add(src)
                        print(f"Downloading image from URL: {src}")
                        img_data = requests.get(src, timeout=10)
                        img_data.raise_for_status()

                        file_extension = os.path.splitext(src.split("?")[0])[-1]
                        if not file_extension or len(file_extension) > 5:
                            file_extension = '.jpg'

                        file_name = f"{search_term.replace(' ', '_')}_{downloaded_count + 1}{file_extension}"
                        file_path = os.path.join(save_folder, file_name)

                        with open(file_path, 'wb') as img_file:
                            img_file.write(img_data.content)

                        print(f"Saved image to: {file_path}")
                        downloaded_count += 1
                        print(f"Downloaded {downloaded_count}/{num_images} images.")

                        if downloaded_count >= num_images:
                            break
            except Exception as e:
                print(f"Error downloading image: {e}")
        
        # Scroll down to load more images if needed
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        time.sleep(2)

    driver.quit()
    print(f"Downloaded {downloaded_count} images to {save_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from Google Images.")
    parser.add_argument('search_term', type=str, help='The search term to use for finding images.')
    parser.add_argument('num_images', type=int, help='The number of images to download.')
    parser.add_argument('save_folder', type=str, help='The folder where images will be saved.')

    args = parser.parse_args()

    print("Starting image download...")
    download_images(args.search_term, args.num_images, args.save_folder)
    print("Image download completed.")
