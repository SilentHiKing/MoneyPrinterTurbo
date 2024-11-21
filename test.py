import os
import glob

import ffmpeg
from moviepy.video.compositing.concatenate import concatenate_videoclips

from app.models.schema import VideoAspect, VideoConcatMode
from app.services import video
import os
from moviepy.editor import VideoFileClip


def get_mp4_files_sorted_by_creation_time(folder_path):
    # 使用 glob 查找所有以 .mp4 结尾的文件
    mp4_files = glob.glob(os.path.join(folder_path, '*.mp4'))

    # 按文件的创建时间排序 (使用 os.path.getctime 获取文件创建时间)
    mp4_files_sorted = sorted(mp4_files, key=os.path.getctime)

    return mp4_files_sorted


def get_mp4():
    # 示例：指定文件夹路径
    folder_path = r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\comfyui_pic'  # 替换为你的文件夹路径
    mp4_files = get_mp4_files_sorted_by_creation_time(folder_path)
    return mp4_files


def merge_mp4_files_low_memory(mp4_files, output_file):
    # 创建一个临时文件作为中间合并结果的输出
    temp_output = "temp_merge.mp4"

    # 遍历文件列表，逐个拼接
    with open(temp_output, 'wb') as f_out:
        for idx, file in enumerate(mp4_files):
            with open(file, 'rb') as f_in:
                if idx == 0:
                    # 如果是第一个文件，直接写入
                    f_out.write(f_in.read())
                else:
                    # 如果不是第一个文件，需要忽略后续视频中的文件头（header）
                    f_in.seek(1, os.SEEK_SET)  # 跳过文件头部分，避免重复
                    f_out.write(f_in.read())

    # 将临时文件转码为最终输出的MP4格式
    final_clip = VideoFileClip(temp_output)
    final_clip.write_videofile(output_file, codec="libx264")

    # 删除临时文件
    os.remove(temp_output)


def merge_mp4_files(mp4_files, output_file):
    # 加载所有的 MP4 文件为 VideoFileClip 对象
    clips = [VideoFileClip(file) for file in mp4_files]

    # 将所有的剪辑合并在一起
    final_clip = concatenate_videoclips(clips)

    # 将合并后的剪辑导出为一个新的 MP4 文件
    final_clip.write_videofile(output_file, codec="libx264")

    # 关闭所有剪辑文件
    for clip in clips:
        clip.close()


import os
import subprocess


def merge_mp4_files_ffmpeg(mp4_files, output_file):
    ffmpeg_path = r'D:\Install\ffmpeg-7.0.2-essentials_build\bin\ffmpeg.exe'

    # 创建一个临时的文件，存储待合并文件的路径
    file_list = 'mp4_files_list.txt'

    with open(file_list, 'w') as f:
        for mp4 in mp4_files:
            # ffmpeg 需要路径前加 "file" 关键字
            f.write(f"file '{os.path.abspath(mp4)}'\n")

        # 使用ffmpeg合并视频文件
    try:
        (
            ffmpeg
            .input(file_list, format='concat', safe=0)
            .output(output_file, c='copy')
            .run(cmd=ffmpeg_path, overwrite_output=True)
        )
        print(f"视频合并成功，保存为: {output_file}")
    except ffmpeg.Error as e:
        print(f"视频合并失败: {e.stderr.decode()}")

        # 删除临时文件
    if os.path.exists(file_list):
        os.remove(file_list)


def my():
    combined_video_path = r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\combined-1.mp4'
    audio_file = r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\audio.mp3'
    video.combine_videos(
        combined_video_path=combined_video_path,
        video_paths=get_mp4(),
        audio_file=audio_file,
        video_aspect=VideoAspect.landscape,
        video_concat_mode=VideoConcatMode.sequential,
        max_clip_duration=1700,
        threads=1,
    )


def merge_mp4_mp3_srt_with_position(mp4_file, mp3_file, srt_file, output_file, alignment=2):
    try:
        ffmpeg_path = r'D:\Install\ffmpeg-7.0.2-essentials_build\bin\ffmpeg.exe'
        # 分别加载视频和音频的输入
        video_input = ffmpeg.input(mp4_file)  # 输入视频文件
        audio_input = ffmpeg.input(mp3_file)  # 输入音频文件
        # 使用 ffmpeg 合并视频、音频和字幕
        (
            ffmpeg
            .concat(video_input, audio_input, v=1, a=1)  # 合并视频和音频流
            .output(output_file, codec='copy', audio_codec='aac', codec_subtitle='mov_text',
                    vf=f"subtitles='{srt_file}':force_style='Alignment={alignment}'")
            .run(cmd=ffmpeg_path, overwrite_output=True)
        )
        print(f"视频、音频、字幕合并成功，保存为: {output_file}")
    except ffmpeg.Error as e:
        print(f"合并失败: {e.stderr.decode()}")


# 使用示例
# merge_mp4_mp3_srt_with_position(r'D:\AI\MoneyPrinterTurbo\merged_video.mp4',
#                                 r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\audio.mp3',
#                                 r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\subtitle.srt',
#                                 'output.mp4')


# 输出文件的名称
output_file = 'merged_video.mp4'


# 调用合并函数
# merge_mp4_files_ffmpeg(get_mp4(), output_file)

# print(f"MP4 文件合并完成，输出文件: {output_file}")




