import os
import youtube_dl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import subprocess

def get_clip_links(driver):
   driver.get("https://www.twitch.tv/directory/category/rocket-league/clips")
   driver.implicitly_wait(10)

   links = driver.find_elements(By.XPATH, "//a[@data-a-target='preview-card-image-link']")[:4]
   clip_links = [link.get_attribute('href') for link in links]
   return clip_links

def download_clip(url, filename):
   ydl_opts = {
       'outtmpl': filename,
   }
   with youtube_dl.YoutubeDL(ydl_opts) as ydl:
       ydl.download([url])

def create_video_from_clips(clip_links):
   with open('assets/clips.txt', 'w') as f:
       for i in range(len(clip_links)):
           f.write(f"file 'clips/clip{i}.mp4'\n")

   command = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'assets/clips.txt', '-c', 'copy', 'assets/output.mp4']
   subprocess.run(command, check=True)

   delete_clips(clip_links)

def delete_clips(clip_links):
   for i in range(len(clip_links)):
       clip_filename = f'assets/clips/clip{i}.mp4'
       if os.path.isfile(clip_filename):
           os.remove(clip_filename)

def main():
   driver = webdriver.Chrome()
   clip_links = get_clip_links(driver)

   if not os.path.exists('assets/clips'):
       os.makedirs('assets/clips')

   with ThreadPoolExecutor(max_workers=5) as executor:
       for i, clip_link in enumerate(clip_links):
           executor.submit(download_clip, clip_link, f'assets/clips/clip{i}.mp4')

   create_video_from_clips(clip_links)
   driver.quit()

if __name__ == "__main__":
   main()
