import os.path
import re

import unicodedata

from app.utils import utils


def time_to_milliseconds(time_str):
    # 分割时间字符串，小时:分钟:秒,毫秒 如"00:00:13,562"
    h, m, s_ms = time_str.split(':')
    s, ms = s_ms.split(',')

    # 将时间转换为毫秒
    total_ms = (int(h) * 3600 * 1000) + (int(m) * 60 * 1000) + (int(s) * 1000) + int(ms)

    return total_ms


def is_period(char):
    return unicodedata.category(char) == 'Po' and 'FULL STOP' in unicodedata.name(char)


def is_punctuation(char):
    char = char[-1]
    # 使用 unicodedata.category 判断字符是否是标点符号
    return unicodedata.category(char).startswith('P')


def is_slice_end(txt) -> bool:
    if len(txt) == 0:
        return True
    _last_chat = txt[-1]
    if not is_punctuation(_last_chat) and (_last_chat == '\n'):
        return True
    if is_period(_last_chat):
        return True
    if unicodedata.category(_last_chat) == 'Pf' or unicodedata.category(_last_chat) == 'Pe':
        return True
    return False


def is_slice_end_pic(txt, max_size=200, min_size=30):
    if (is_slice_end(txt) and (len(txt) > min_size)) or len(txt) > max_size:
        return True
    return False


def extract_srt_content(srt_text, max_size=200, min_size=30):
    # 正则表达式匹配时间戳和文本
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?=\n\n|\Z)'

    matches = re.findall(pattern, srt_text, re.MULTILINE)
    extracted_data = []

    start_tag = -1
    end_tag = -1
    temp = ''
    # 遍历提取结果并输出
    for match in matches:
        subtitle_number = match[0]
        start_time = match[1]
        end_time = match[2]
        content = match[3].replace('\n', '').strip()
        temp = f"{temp}{content}"
        end_tag = time_to_milliseconds(end_time.strip())
        if start_tag == -1:
            start_tag = time_to_milliseconds(start_time.strip())

        if is_slice_end_pic(temp, max_size, min_size):
            extracted_data.append({
                'number': subtitle_number,
                'start_time': start_tag,
                'end_time': end_tag,
                'text': temp
            })
            temp = ''
            start_tag = -1
    if temp:
        extracted_data.append({
            'number': matches[-1][0],
            'start_time': start_tag,
            'end_time': end_tag,
            'text': temp
        })
    # 打印结果
    for item in extracted_data:
        print(f"字幕号: {item['number']}")
        print(f"开始时间: {item['start_time']}")
        print(f"结束时间: {item['end_time']}")
        print(f"文本: {item['text']}")
        print()
    return extracted_data


def read_srt_file(srt_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_dir_comfyui_pic(client_id):
    path = os.path.join(utils.task_dir(client_id), "comfyui_pic")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


if __name__ == "__main__":
    path = os.path.join(utils.storage_dir(), "tasks", "1c1011eb-044c-4869-9928-1e51a473aeb8", "subtitle.srt")
    print(f"path{path}")
    # 示例字幕文本
    subtitle_text = read_srt_file(path)

    extracted_data = extract_srt_content(subtitle_text)
    # 打印结果
    for item in extracted_data:
        print(f"字幕号: {item['number']}")
        print(f"开始时间: {item['start_time']}")
        print(f"结束时间: {item['end_time']}")
        print(f"文本: {item['text']}")
        print()
