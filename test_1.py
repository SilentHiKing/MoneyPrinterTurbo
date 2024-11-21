import os
import glob

import ffmpeg
from moviepy.video.compositing.concatenate import concatenate_videoclips

from app.models.schema import VideoAspect, VideoConcatMode
from app.services import video
import os
from moviepy.editor import *

def run_resize():
    print(f"Video size: ")
    clip = VideoFileClip(r'"D:\AI\MoneyPrinterTurbo\storage\tasks\9b4c0dbd-6423-4f77-a19b-7f29507144bc\4. 大人世界与小王子的隔阂.mp4"').without_audio()
    # 检查视频的基本属性
    print(f"Video size: {clip.size}")  # 输出视频的原始大小
    print(f"Duration: {clip.duration}")  # 输出视频时长




if __name__ == '__main__':
    run_resize()

