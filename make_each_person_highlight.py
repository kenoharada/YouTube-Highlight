import cv2
import moviepy.editor as mp
from pydub import AudioSegment
import subprocess


def check_faces(record_path, frames_threshold=10):
    with open(record_path) as f:
        img_paths = set(f.read().split('\n')[:-1])
        img_paths = sorted(list(img_paths))
    verified_img_paths = []
    buffer = []
    last_path = img_paths[0]
    buffer.append(last_path)
    for img_path in img_paths[1:]:
        if int(img_path.split('img_')[-1].replace('.png', '')) == int(last_path.split('img_')[-1].replace('.png', '')) + 1:
            buffer.append(img_path)
        else:
            if len(buffer) > frames_threshold:
                verified_img_paths += buffer
            buffer = []
            buffer.append(img_path)
        last_path = img_path
    verified_img_paths_txt = record_path.replace('.txt', '_verified.txt')
    if len(verified_img_paths) > 0:
        with open(verified_img_paths_txt, 'a') as f:
            for verified_img_path in verified_img_paths:
                f.write(f'{verified_img_path}\n')
        return verified_img_paths_txt
    else:
        return None


def make_video(verified_img_paths_txt, input_video='summary.mp4'):
    output_video_path = verified_img_paths_txt.replace('.txt', '.mp4')
    with open(verified_img_paths_txt) as f:
        img_paths = sorted(f.read().split('\n')[:-1])
    
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    cap = cv2.VideoCapture(input_video)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vw = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    for img_path in img_paths:
        img = cv2.imread(f'imgs/{img_path}')
        vw.write(img)
    vw.release()


def retrieve_audio(video_path, output_audio_path='audio.mp3'):
    clip_input = mp.VideoFileClip(video_path).subclip()
    clip_input.audio.write_audiofile(output_audio_path)


def pick_audio(verified_img_paths, audio_path='audio.mp3'):
    sourceAudio = AudioSegment.from_mp3(audio_path)
    with open(verified_img_paths) as f:
        img_path_list = sorted(list(set(f.read().split('\n')[:-1])))
    last_path = img_path_list[0]
    start_frame_num = int(last_path.split('img_')[-1].replace('.png', ''))
    end_frame_num = start_frame_num
    audio_list = []
    total_sound = AudioSegment.empty()
    for img_path in img_path_list[1:]:
        if int(img_path.split('img_')[-1].replace('.png', '')) == int(last_path.split('img_')[-1].replace('.png', '')) + 1:
            end_frame_num = int(img_path.split('img_')[-1].replace('.png', ''))
            last_path = img_path
        else:
            # sourceAudioの1slice = 1ms
            # 30fpsで切り出された 1fps = 1000/23 ms = 33ms
            total_sound += sourceAudio[43*start_frame_num:43*end_frame_num]
            start_frame_num = int(img_path.split('img_')[-1].replace('.png', ''))
            last_path = img_path
    if start_frame_num < end_frame_num:
        total_sound += sourceAudio[43*start_frame_num:43*end_frame_num]
    audio_file_path = verified_img_paths.replace('.txt', '.mp3')
    total_sound.export(audio_file_path, format="mp3")


def sec_to_time(sec):
    hh = int(sec // 3600)
    mm = int((sec - (3600 * hh)) // 60)
    ss_ms = round(sec - (3600 * hh + mm * 60), 2)
    fill = '' if ss_ms >= 10 else '0'
    time = f'{str(hh).zfill(2)}:{str(mm).zfill(2)}:{fill}{ss_ms}'
    return time

def cut_movie(verified_img_paths, video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    with open(verified_img_paths) as f:
        img_path_list = sorted(list(set(f.read().split('\n')[:-1])))
    last_path = img_path_list[0]
    start_s = round(int(last_path.split('img_')[-1].replace('.png', '')) / fps, 2)
    start_time = sec_to_time(start_s)
    end_s = start_s
    file_path = '/'.join(verified_img_paths.split('/')[:-1]) + '/file_list.txt'
    print(file_path)
    for img_path in img_path_list[1:]:
        if int(img_path.split('img_')[-1].replace('.png', '')) == int(last_path.split('img_')[-1].replace('.png', '')) + 1:
            end_s = round(int(img_path.split('img_')[-1].replace('.png', '')) / fps, 2)
            end_time = sec_to_time(end_s)
            last_path = img_path
        else:
            path_name = '_'.join(start_time.split(':')) + '_'.join(end_time.split(':'))
            output_path = verified_img_paths.replace('.txt', f'_{path_name}.mp4')
            subprocess.run(f'ffmpeg -ss {start_time} -i {video_path} -t {end_s - start_s} {output_path}', shell=True)
            with open(file_path, 'a') as f:
                f.write(f'file {output_path.split("/")[-1]}\n')
            start_s = round(int(img_path.split('img_')[-1].replace('.png', '')) / fps, 2)
            start_time = sec_to_time(start_s)
            last_path = img_path
    if start_s < end_s:
        path_name = '_'.join(start_time.split(':')) + '_'.join(end_time.split(':'))
        output_path = verified_img_paths.replace('.txt', f'_{path_name}.mp4')
        subprocess.run(f'ffmpeg -ss {start_time} -i {video_path} -t {end_s - start_s} {output_path}', shell=True)
        with open(file_path, 'a') as f:
            f.write(f'file {output_path.split("/")[-1]}\n')
    result_movie_path = '/'.join(verified_img_paths.split('/')[:-1]) + '/result.mp4'
    subprocess.run(f'ffmpeg -f concat -i {file_path} {result_movie_path}', shell=True)


    



if __name__ == "__main__":
    import glob
    import argparse
    txt_paths = glob.glob('results/id_*/records.txt')
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    parser = argparse.ArgumentParser()
    parser.add_argument('--ytid', type=str, required=True)
    args = parser.parse_args()
    input_video = f'{args.ytid}/summary.mp4'
    for txt_path in txt_paths:
        verified_img_paths_txt = check_faces(txt_path)
        if verified_img_paths_txt:
            cut_movie(verified_img_paths_txt, input_video)


    # retrieve_audio('summary.mp4')
    # pick_audio('results/id_2/records_verified.txt')
    # cut_movie('results/id_8/records_verified.txt', 'summary.mp4')
    # file_path = 'results/id_2/file_list.txt'
    # result_movie_path = 'results/id_2/result.mp4'
    # subprocess.run(f'ffmpeg -f concat -i {file_path} -c copy {result_movie_path}', shell=True)
    