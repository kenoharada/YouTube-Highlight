import requests
import json
from bs4 import BeautifulSoup
import glob
import subprocess
import os


URL = 'https://www.googleapis.com/youtube/v3/'
# ここにAPI KEYを入力
API_KEY = ''

def dl_comment_to_json(video_id):
    params = {
        'key': API_KEY,
        'part': 'snippet',
        'videoId': video_id,
        'order': 'relevance',
        'textFormat': 'html',
        'maxResults': 3000,
        'pageToken': ''
    }
    response = requests.get(URL + 'commentThreads', params=params)
    resource = response.json()
    c = 0
    os.makedirs(f'yt_{video_id}', exist_ok=True)
    with open(f'yt_{video_id}/{c}_html.json', mode='wt', encoding='utf-8') as file:
        json.dump(resource, file, ensure_ascii=False, indent=2)
    # c += 1
    # while resource['nextPageToken'] != '':
    #     params['pageToken'] = resource['nextPageToken']
    #     response = requests.get(URL + 'commentThreads', params=params)
    #     resource = response.json()
    #     with open(f'{video_id}_{c}_html.json', mode='wt', encoding='utf-8') as file:
    #         json.dump(resource, file, ensure_ascii=False, indent=2)
    #     c += 1

def retrive_timestamp(video_id):
    file_list = glob.glob(f"{video_id}/*.json")
    comment_file = f'{video_id}/comment.txt'

    for json_file in file_list:
        with open(json_file) as f:
            data = json.load(f)


        for comment_info in data['items']:
            # コメント
            text_display = comment_info['snippet']['topLevelComment']['snippet']['textDisplay']
            soup = BeautifulSoup(text_display, 'html.parser')
            links = soup.find_all('a')
            # print(links)
            if len(links) > 0:
                for link in links:
                    # print(link.text, 'text')
                    with open(comment_file, 'a') as f:
                        comment = comment_info['snippet']['topLevelComment']['snippet']['textOriginal'].replace('\n', '')
                        f.write(f"{link.text}, {comment}\n")


def dl_youtube(youtube_url, video_id):
    dl_cmd = f'youtube-dl {youtube_url} --merge-output-format mp4 -o {video_id}/dl.mp4'
    subprocess.run(dl_cmd, shell=True)


def cut_movie(video_id):
    time_list = []
    os.makedirs(f'{video_id}/movie', exist_ok=True)
    with open(f'{video_id}/comment.txt') as f:
        comments = f.read().split('\n')[:-1]
        for comment in comments:
            time_stamp = comment.split(', ')[0]
            time = time_stamp.split(':')
            time_ = int(time[0]) * 60 + int(time[1])
            start_time = time_ - 1 if time_ - 1 > 0 else time_
            end_time = time_ + 4

            start_time = [
                '00', 
                str(start_time // 60) if int(start_time // 60) >= 10 else '0'+str(start_time // 60),
                str(start_time % 60) if int(start_time % 60) >= 10 else '0'+str(start_time % 60)
            ]
            end_time = [
                '00', 
                str(end_time // 60) if int(end_time // 60) >= 10 else '0'+str(end_time // 60),
                str(end_time % 60) if int(end_time % 60) >= 10 else '0'+str(end_time % 60)
            ]
            if time_ in time_list:
                continue
            try:
                cut_cmd = f"ffmpeg -i {video_id}/dl.mp4 -ss {':'.join(start_time)} -to {':'.join(end_time)} {video_id}/movie/file_{':'.join(start_time)}.mp4"
                subprocess.run(cut_cmd, shell=True)
            except:
                print(time_)
            time_list.append(time_)
            time_list.append(time_ - 1)
            time_list.append(time_ + 1)


def concat_movie(video_id):

    file_list = sorted(glob.glob(f"{video_id}/movie/*.mp4"))

    for mp4 in file_list:
        file_name = mp4.replace(f'{video_id}/', '')
        with open(f'{video_id}/file_name.txt', 'a') as f:
            f.write(f'file {file_name}\n')

    subprocess.run(f'ffmpeg -f concat -safe 0 -i {video_id}/file_name.txt -c copy {video_id}/summary.mp4', shell=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True)
    args = parser.parse_args()
    # url = 'https://www.youtube.com/watch?v=hogehoge'
    video_id = args.url.replace('https://www.youtube.com/watch?v=', '')
    dl_comment_to_json(video_id)
    video_id = 'yt_' + video_id
    retrive_timestamp(video_id)
    dl_youtube(youtube_url=args.url, video_id=video_id)
    cut_movie(video_id)
    concat_movie(video_id)
    subprocess.run(f'ffmpeg -f concat -safe 0 -i {video_id}/file_name.txt -c copy {video_id}/summary.mp4', shell=True)

