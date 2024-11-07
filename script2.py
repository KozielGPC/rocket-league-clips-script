import os
import youtube_dl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import subprocess
import json

def get_clip_links(driver):
    driver.get("https://www.twitch.tv/directory/category/rocket-league/clips?range=all")
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



def analyze_clip(filename):
    # Use ffprobe to get video and audio stream information
    command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', filename]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        # Parse ffprobe output and return width, height, and codec type
        data = json.loads(result.stdout)
        streams = data.get('streams', [])

        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)

        if video_stream and audio_stream:
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
            codec_type = video_stream.get('codec_name', '')

            return width, height, codec_type
        else:
            raise RuntimeError(f"Video or audio stream not found in clip {filename}")
    else:
        raise RuntimeError(f"Failed to analyze clip {filename}")


def adjust_clip_configuration(input_filename, output_filename, width, height, codec_type):
    # Use ffmpeg to adjust the video and audio configurations
    command = ['ffmpeg', '-i', input_filename, '-vf', f'scale={width}:{height}', '-c:a', 'copy', output_filename]
    subprocess.run(command, check=True)

def create_video_from_clips(clip_links):
    clip_info = []

    print('================ Analyzing clips ==================')
    with open('assets/clips.txt', 'w') as f:
        for i, clip_link in enumerate(clip_links):
            input_filename = f'assets/clips/clip{i}.mp4'
            clip_info.append(analyze_clip(input_filename))
            f.write(f"file '{input_filename}'\n")

    # Get the common video and audio configurations from the first clip
    width, height, codec_type = clip_info[0]

    print('================ Cips analyzed!!! ==================')
    
    print('\n')
    
    print('================ Adjusting clips ==================')
    # Adjust the configurations of all clips
    for i, clip_link in enumerate(clip_links):
        input_filename = f'assets/clips/clip{i}.mp4'
        output_filename = f'assets/clips/adjusted_clip{i}.mp4'
        adjust_clip_configuration(input_filename, output_filename, width, height, codec_type)

    print('================ Cips adjusted!!! ==================')
    
    print('\n')
    
    print('================ Creating video from clips ==================')
    # Concatenate the adjusted clips
    with open('assets/adjusted_clips.txt', 'w') as f:
        for i in range(len(clip_links)):
            f.write(f"file 'clips/adjusted_clip{i}.mp4'\n")


    command = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'assets/adjusted_clips.txt', '-c', 'copy', 'assets/output.mp4']
    subprocess.run(command, check=True)

    print('================ Video created!!! ==================')
    
    print('\n')
    
    print('================ Deleting clips ==================')
    delete_clips(clip_links)
    
    print('================ Cips deleted!!! ==================')

def delete_clips(clip_links):
    for i in range(len(clip_links)):
        clip_filename = f'assets/clips/clip{i}.mp4'
        adjusted_clip_filename = f'assets/clips/adjusted_clip{i}.mp4'

        if os.path.isfile(clip_filename):
            os.remove(clip_filename)

        if os.path.isfile(adjusted_clip_filename):
            os.remove(adjusted_clip_filename)

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
