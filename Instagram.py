from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
import re
import random

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def login_to_instagram(username, password):
    print("Logging in to Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
    time.sleep(8)
    # Handle "Save Info" prompt
    try:
        driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]").click()
        time.sleep(2)
    except:
        pass

def get_profile_pic(profile_username):
    print("Downloading profile picture...")
    driver.get(f"https://www.instagram.com/{profile_username}/")
    time.sleep(3)
    try:
        profile_img = driver.find_element(By.XPATH, "//header//img")
        img_url = profile_img.get_attribute('src')
        download_media(img_url, f"downloads/{profile_username}_profile.jpg")
    except Exception as e:
        print(f"Failed to get profile picture: {e}")

def scroll_to_bottom_collect_post_links():
    print("Collecting post links...")
    post_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    while scroll_attempts < 5:
        posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
        for post in posts:
            href = post.get_attribute('href')
            if "/p/" in href:
                post_links.add(href.split("?")[0])  # Clean URL

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            last_height = new_height

    return list(post_links)

def download_media(url, filename):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
            return True
        else:
            print(f"Failed to download: {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def get_high_quality_media():
    """Get HD media from meta tags"""
    try:
        # Check for video first
        video_tag = driver.find_element(By.XPATH, '//meta[@property="og:video"]')
        if video_tag:
            return video_tag.get_attribute('content'), 'video'
    except:
        pass
    
    try:
        # Then check for image
        img_tag = driver.find_element(By.XPATH, '//meta[@property="og:image"]')
        if img_tag:
            return img_tag.get_attribute('content'), 'image'
    except:
        pass
    
    return None, None

def download_highlights(profile_username):
    print("Downloading highlights...")
    driver.get(f"https://www.instagram.com/{profile_username}/")
    time.sleep(3)
    
    # Find highlights
    try:
        highlights = driver.find_elements(By.XPATH, "//a[contains(@href, '/stories/highlights/')]")
        print(f"Found {len(highlights)} highlights")
        
        for i, highlight in enumerate(highlights):
            highlight_url = highlight.get_attribute('href')
            driver.get(highlight_url)
            time.sleep(4)
            
            # Create directory for this highlight
            highlight_name = f"highlight_{i+1}"
            os.makedirs(f"downloads/highlights/{highlight_name}", exist_ok=True)
            
            story_count = 0
            while True:
                story_count += 1
                # Get current story media
                media_url, media_type = get_high_quality_media()
                if media_url:
                    ext = 'mp4' if media_type == 'video' else 'jpg'
                    download_media(
                        media_url, 
                        f"downloads/highlights/{highlight_name}/story_{story_count}.{ext}"
                    )
                
                # Try to move to next story
                try:
                    driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next')]").click()
                    time.sleep(2)
                except:
                    break  # No more stories
                    
            driver.back()
            time.sleep(2)
    except Exception as e:
        print(f"Error downloading highlights: {e}")

def download_random_commenter_pics(post_links, num_pics=5):
    print("Downloading random commenter profile pictures...")
    os.makedirs("downloads/commenters", exist_ok=True)
    
    # Select random posts
    random_posts = random.sample(post_links, min(num_pics, len(post_links)))
    
    for post_url in random_posts:
        driver.get(post_url)
        time.sleep(3)
        
        # Load comments
        try:
            driver.find_element(By.XPATH, "//div[contains(text(), 'comments')]").click()
            time.sleep(2)
        except:
            pass
        
        # Get commenter profile images
        try:
            commenters = driver.find_elements(By.XPATH, "//ul/div/li/div/div/div/div/div/a")
            for commenter in commenters:
                try:
                    img = commenter.find_element(By.TAG_NAME, "img")
                    img_url = img.get_attribute('src')
                    username = commenter.get_attribute('href').split("/")[3]
                    if img_url and username:
                        download_media(
                            img_url, 
                            f"downloads/commenters/{username}.jpg"
                        )
                        # Stop after first valid download per post
                        break  
                except:
                    continue
        except Exception as e:
            print(f"Error getting commenters: {e}")

def visit_each_post_and_download(post_links):
    print("Downloading posts...")
    os.makedirs("downloads/posts", exist_ok=True)
    
    for index, link in enumerate(post_links):
        print(f"Processing post {index+1}/{len(post_links)}")
        driver.get(link)
        time.sleep(3)
        
        # Get high-quality media
        media_url, media_type = get_high_quality_media()
        if media_url:
            ext = 'mp4' if media_type == 'video' else 'jpg'
            download_media(
                media_url, 
                f"downloads/posts/post_{index+1}.{ext}"
            )

def main():
    # Use environment variables or input for credentials
    username = 'am.priyanshu006'  # Replace with actual
    password = '9818000895'  # Replace with actual
    profile_username = 'ananya_557singh'  # Replace with actual
    
    # Create main download directory
    os.makedirs("downloads", exist_ok=True)
    
    login_to_instagram(username, password)
    from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def login_to_instagram(username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
    time.sleep(10)

def scroll_to_bottom_collect_post_links():
    post_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    while True:
        posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
        for post in posts:
            post_links.add(post.get_attribute('href'))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            if scroll_attempts > 3:  # scrolled to end
                break
        else:
            scroll_attempts = 0
            last_height = new_height

    return list(post_links)

def download_media(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def visit_each_post_and_download(post_links):
    os.makedirs("downloads", exist_ok=True)
    for index, link in enumerate(post_links):
        driver.get(link)
        time.sleep(5)

        # Download all images
        images = driver.find_elements(By.XPATH, '//article//img')
        for i, img in enumerate(images):
            img_url = img.get_attribute('src')
            if img_url:
                filename = f"downloads/post_{index+1}_img{i+1}.jpg"
                download_media(img_url, filename)

        # Download all videos
        videos = driver.find_elements(By.XPATH, '//article//video')
        for j, vid in enumerate(videos):
            vid_url = vid.get_attribute('src')
            if vid_url:
                filename = f"downloads/post_{index+1}_video{j+1}.mp4"
                download_media(vid_url, filename)

def main():
    username = 'am.priyanshu006'
    password = 'xxpxpxpx'
    profile_username = 'ananya_557singh'

    login_to_instagram(username, password)
    driver.get(f"https://www.instagram.com/{profile_username}/")
    time.sleep(5)

    post_links = scroll_to_bottom_collect_post_links()
    print(f"Found {len(post_links)} posts")
    visit_each_post_and_download(post_links)

    input("Press Enter to quit...")
    driver.quit()

if __name__ == "__main__":
    main()

    # Download profile pic
    get_profile_pic(profile_username)
    
    # Navigate to profile
    driver.get(f"https://www.instagram.com/{profile_username}/")
    time.sleep(3)
    
    # Get posts
    post_links = scroll_to_bottom_collect_post_links()
    print(f"Found {len(post_links)} posts")
    
    # Download content
    visit_each_post_and_download(post_links)
    download_highlights(profile_username)
    download_random_commenter_pics(post_links, num_pics=10)  # Adjust as needed
    
    print("Download completed!")
    driver.quit()

if __name__ == "__main__":
    main()