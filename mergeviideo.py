import ffmpeg
import os
import subprocess

# 设置 FFmpeg 可执行文件的路径
ffmpeg_path = r'D:\Install\ffmpeg-7.0.2-essentials_build\bin\ffmpeg.exe'
ffprobe_path = r'D:\Install\ffmpeg-7.0.2-essentials_build\bin\ffprobe.exe'


def get_duration(file_path):
    """使用 FFprobe 获取媒体文件的持续时间"""
    cmd = [ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
           file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout)


def merge_video_audio_subtitle(video_path, audio_path, subtitle_path, output_path):
    # 获取视频和音频的时长
    video_duration = get_duration(video_path)
    audio_duration = get_duration(audio_path)

    # 步骤1：合并视频和音频
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)

    # 如果音频比视频长，裁剪音频；如果音频比视频短，循环音频
    if audio_duration > video_duration:
        input_audio = input_audio.filter('atrim', duration=video_duration)
    elif audio_duration < video_duration:
        input_audio = input_audio.filter('aloop', loop=-1, size=audio_duration).filter('atrim', duration=video_duration)

    merged = ffmpeg.output(input_video, input_audio, 'temp_merged.mp4', vcodec='libx264', acodec='aac')
    ffmpeg.run(merged, cmd=ffmpeg_path, overwrite_output=True)




# 使用示例
video_file = r'D:\AI\MoneyPrinterTurbo\merged_video.mp4'
audio_file = r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\audio.mp3'
subtitle_file = r'D:\AI\MoneyPrinterTurbo\storage\tasks\57efde1c-2254-4c7f-b3b0-da4bd2d63804\subtitle.srt'
output_file = "output_video.mp4"

merge_video_audio_subtitle(video_file, audio_file, subtitle_file, output_file)
print(f"合并完成，输出文件：{output_file}")