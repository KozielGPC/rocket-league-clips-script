import os
import youtube_dl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_clip_links(driver):
    driver.get("https://www.twitch.tv/directory/game/Rocket%20League/clips?fbclid=IwAR2xYPFh3Um2YS4EsDkjAdA0b-CMvjQTLVLeNW5D77-aPh3IqwW9c4e7lIM&range=24hr")
    driver.implicitly_wait(10)

    links = driver.find_elements(By.XPATH, "//a[@data-a-target='preview-card-image-link']")[:10]
    clip_links = [link.get_attribute('href') for link in links]
    return clip_links

def download_clip(url, filename):
    ydl_opts = {
        'outtmpl': filename,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def create_video_from_clips(clip_links):
    clips = [VideoFileClip(f'clips/clip{i}.mp4') for i in range(len(clip_links))
             if os.path.isfile(f'clips/clip{i}.mp4')]  

    final_clip = concatenate_videoclips(clips)

    final_clip.write_videofile("output.mp4")
    delete_clips(clip_links)  

def delete_clips(clip_links):
    for i in range(len(clip_links)):
        clip_filename = f'clips/clip{i}.mp4'
        if os.path.isfile(clip_filename):
            os.remove(clip_filename)

def main():
    driver = webdriver.Chrome()
    clip_links = get_clip_links(driver)

    if not os.path.exists('clips'):
        os.makedirs('clips')

    for i, clip_link in enumerate(clip_links):
        download_clip(clip_link, f'clips/clip{i}.mp4')

    create_video_from_clips(clip_links)
    driver.quit()

if __name__ == "__main__":
    main()
