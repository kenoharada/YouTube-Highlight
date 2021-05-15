## YouTube Highlight
Extract highlights from YouTube videos and create a summary for each character.
The videos produced by this software can be used by YouTubers to gain more fans, and by individuals to more efficiently review the videos of the creators they support.

## Requirements
- ffmpeg
- opencv
- youtube-dl
- BeautifulSoup

## How to use
1. Get API key to retrive the comments on YouTube Video, and set API_KEY in url_to_highlight.py

https://developers.google.com/youtube/v3/getting-started?hl=ja

2. Choose video you want to highlight from, and prepare that video's URL

e.g) https://www.youtube.com/watch?v=hogehoge

3. run url_to_highlight.py, the output will be saved yt_{hogehoge} dir, yt_{hogehoge}/summary.mp4 is highlight of the video

`$ python url_to_highlight.py --url https://www.youtube.com/watch?v=hogehoge`

4. run distinguish.py, this uses deep learning module, so run on GPU is recommended

`$ python distinguish.py --ytid yt_{hogehoge}`

5. run make_each_person_highlight.py, the ouput will be saved in results dir

`$ python make_each_person_highlight.py --ytid yt_{hogehoge}`

## Acknowledgements
This repo's face recognition function is on [FaceX-Zoo](https://github.com/JDAI-CV/FaceX-Zoo).
I modify face_sdk module in the FaceX-Zoo to detect and recognize faces.
I really appreciate their valuable efforts.

This project is for final project of [FSDL(Full Stack Deep Learning)](https://fullstackdeeplearning.com/).
I learned a lot from this course, thank you very much for offering.


