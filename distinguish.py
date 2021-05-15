import sys
sys.path.append('face_sdk')
from face_sdk.api_usage.face_models import get_models

faceDetModelHandler, faceAlignModelHandler, faceRecModelHandler, face_cropper = get_models()
import cv2
import numpy as np
import os
import argparse

def get_query_features(query_image):
    dets = faceDetModelHandler.inference_on_image(query_image)
    face_nums = dets.shape[0]
    feature_list = []
    if face_nums > 0:
        for i in range(face_nums):
            landmarks = faceAlignModelHandler.inference_on_image(query_image, dets[i])
            landmarks_list = []
            for (x, y) in landmarks.astype(np.int32):
                landmarks_list.extend((x, y))
            cropped_image = face_cropper.crop_image_by_mat(query_image, landmarks_list)
            feature = faceRecModelHandler.inference_on_image(cropped_image)
            feature_list.append(feature)
            os.makedirs(f'results/id_{i}', exist_ok=True)
            cv2.imwrite(f'results/id_{i}/query.png', cropped_image)
        return feature_list
    else:
        return feature_list


def judge(query_features, target_frame, threshold=0.2):
    dets = faceDetModelHandler.inference_on_image(target_frame)
    face_nums = dets.shape[0]
    id_list = []
    feature_list = []
    cropped_images = []
    for i in range(face_nums):
        landmarks = faceAlignModelHandler.inference_on_image(target_frame, dets[i])
        landmarks_list = []
        for (x, y) in landmarks.astype(np.int32):
            landmarks_list.extend((x, y))
        cropped_image = face_cropper.crop_image_by_mat(target_frame, landmarks_list)
        cropped_images.append(cropped_image)
        feature = faceRecModelHandler.inference_on_image(cropped_image)
        feature_list.append(feature)

    for i in range(len(feature_list)):
        scores = np.dot(np.array(query_features).reshape(-1, 512), feature_list[i].reshape(512, -1))
        max_idx = np.argmax(scores)
        max_score = scores[max_idx]
        if max_score < threshold:
            # make new id
            person_id = len(query_features)
            query_features.append(feature_list[i])
            print('added score was', max_score)
            os.makedirs(f'results/id_{person_id}', exist_ok=True)
            with open(f'results/id_{person_id}/relevant.txt', 'a') as f:
                f.write(f'{max_idx},{max_score}')
            cv2.imwrite(f'results/id_{person_id}/query.png', cropped_images[i])
            max_idx = person_id
        id_list.append(max_idx)
    return id_list


def write_records(id_list, file_path):
    for person_id in id_list:
        with open(f'results/id_{person_id}/records.txt', 'a') as f:
            f.write(f'{file_path}\n')


if __name__ == "__main__":
    c = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('--ytid', type=str, required=True)
    args = parser.parse_args()
    video_path = f'{args.ytid}/summary.mp4'
    os.makedirs('imgs', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_num = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
    fill_num = frame_num + 1
    query_features = []
    while len(query_features) == 0:
        ret, frame = cap.read()
        query_features = get_query_features(frame)
        img_file_name = f'img_{str(c).zfill(fill_num)}.png'
        cv2.imwrite('imgs/' + img_file_name, frame)
        c += 1
    id_list = judge(query_features, frame)
    write_records(id_list, img_file_name)

    while True:
        ret, frame = cap.read()
        if ret:
            id_list = judge(query_features, frame)
            img_file_name = f'img_{str(c).zfill(fill_num)}.png'
            if len(id_list) == 0:
                cv2.imwrite('imgs/' + img_file_name, frame)
            else:
                cv2.imwrite('imgs/' + img_file_name, frame)
                write_records(id_list, img_file_name)
            c += 1
        else:
            break