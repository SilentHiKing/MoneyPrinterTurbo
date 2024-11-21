import os.path
import sys

from app.models.schema import VideoParams, MaterialInfo, MATERIAL_INFO_PROVIDER_COMFYUI
from app.utils import utils, srt_util
from app.services.comfyui import comfyui_normal as comfyui
from app.services import llm, video
from loguru import logger


class Helper(object):
    def __init__(self, task_id):
        self.task_id = task_id

    def read_srt_file(self):
        path = os.path.join(utils.task_dir(self.task_id), "subtitle.srt")
        subtitle_text = srt_util.read_srt_file(path)
        extracted_data = srt_util.extract_srt_content(subtitle_text)
        return extracted_data

    def generate_pics(self):
        extracted_data = self.read_srt_file()
        result = []

        for index, item in enumerate(extracted_data):
            try:
                # 生成翻译文本 "during the late Western Han Dynasty and the Three Kingdoms period"
                translated_text = llm.generate_translate_tip(
                    item['text'],

                )

                # 检查翻译文本是否为空
                if not translated_text:
                    logger.warning(f"Warning: No translation for text at index {index}")
                    translated_text = item['text']  # 使用原始文本作为备用

                # 时间处理逻辑
                start_time = item['start_time']
                end_time = item['end_time']

                if index == 0:
                    start_time = 0
                if index != len(extracted_data) - 1:
                    end_time = extracted_data[index + 1]['start_time']

                # 生成图像路径
                paths = comfyui.generate_clip(self.task_id, translated_text, comfyui.generate_random_seed(),start_time,end_time)
                # 检查路径是否为空
                if not paths or not isinstance(paths, list):
                    logger.warning(f"Error: No image paths generated for text at index {index}")
                    paths = [os.path.join(utils.resource_dir('img'), 'default.png')]  # 使用默认图像路径作为备用

                # 将结果添加到列表
                result.append({
                    'number': item['number'],
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': item['text'],
                    'src_path': paths[0]
                })

                # 调试输出
                # print(f'index_{index} --> img paths: {paths}')
                print(f'index_{index} --> {result[index]}')

            except Exception as e:
                logger.error(f"Error processing item at index {index}: {e}")
                continue

        return result


if __name__ == "__main__":
    helper = Helper("0c01eff7-6b7e-4e62-a97d-b3d3d7ffbeb0")
    # extracted_data = helper.generate_pics()
    extracted_data =[{'number': 3,
                    'start_time': 18087,
                    'end_time': 26800,
                    'text': '那太白金星与美猴王，同出了洞天深处，一齐驾云而起。原来悟空筋斗云比众不同，十分快疾，把个金星撇在脑后.',
                    'src_path': r'D:\AI\MoneyPrinterTurbo\storage\tasks\0c01eff7-6b7e-4e62-a97d-b3d3d7ffbeb0\comfyui_pic\314c1170a24dd3b9d2c002e03a427f9d_1726301876615125.png'}]
    params = VideoParams(video_subject="")
    for item in extracted_data:
        m = MaterialInfo()
        m.provider = MATERIAL_INFO_PROVIDER_COMFYUI
        m.url = item['src_path']
        duration:float = item['end_time'] - item['start_time']
        duration = duration/1000
        print("duration:",duration)
        m.duration = duration
        if not params.video_materials:
            params.video_materials = []
        params.video_materials.append(m)

    params.video_clip_duration= sys.maxsize
    materials = video.preprocess_video(
        materials=params.video_materials, clip_duration=params.video_clip_duration
    )

    # extracted_data = helper.read_srt_file()
    # 打印结果
    for item in extracted_data:
        print(f"字幕号: {item['number']}")
        print(f"开始时间: {item['start_time']}")
        print(f"结束时间: {item['end_time']}")
        print(f"文本: {item['text']}")
        print(f"文件路径: {item['src_path']}")
        print()
