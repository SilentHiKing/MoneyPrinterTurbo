import re


def extract_srt_content(srt_text):
    # 正则表达式匹配时间戳和文本
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?=\n\n|\Z)'

    matches = re.findall(pattern, srt_text, re.MULTILINE)

    extracted_data = []
    for match in matches:
        subtitle_number = match[0]
        start_time = match[1]
        end_time = match[2]
        text = match[3].replace('\n', ' ').strip()

        extracted_data.append({
            'number': subtitle_number,
            'start_time': start_time,
            'end_time': end_time,
            'text': text
        })

    return extracted_data


# 示例使用
srt_content = """
2
00:00:06,275 --> 00:00:10,000
这里的朋友们可以一起探险、体验各种刺激性的游戏，

3
00:00:10,287 --> 00:00:13,000
还可以自由自在地逍遥遥地晒太阳。

4
00:00:13,562 --> 00:00:17,863
每次光临这个奇幻的世外桃源，无不令人充满激动的心情，

"""

result = extract_srt_content(srt_content)

# 打印结果
for item in result:
    print(f"字幕号: {item['number']}")
    print(f"开始时间: {item['start_time']}")
    print(f"结束时间: {item['end_time']}")
    print(f"文本: {item['text']}")
    print()