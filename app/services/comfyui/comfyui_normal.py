import json
import math

import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import urllib.request
import urllib.parse
import random
import os

from loguru import logger

from app.services import llm
from datetime import datetime

from app.config import config
from app.utils import utils, srt_util

server_address = config.app.get("comfyui_url")
workflow_file = os.path.join(os.path.dirname(__file__), 'workflow', config.app.get("comfyui_workflow"))


def generate_random_seed():
    # 生成一个32位整数范围内的随机种子
    random_seed = random.randint(0, 2 ** 32 - 1)

    print(f"Generated Random Seed: {random_seed}")
    return random_seed


# 定义一个函数来显示GIF图片
def show_gif(fname):
    import base64
    from IPython import display
    with open(fname, 'rb') as fd:
        b64 = base64.b64encode(fd.read()).decode('ascii')
    return display.HTML(f'<img src="data:image/gif;base64,{b64}" />')


# 定义一个函数向服务器队列发送提示信息
def queue_prompt(client_id, prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())


# 定义一个函数来获取图片
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()


# 定义一个函数来获取历史记录
def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())


# 定义一个函数来获取图片，这涉及到监听WebSocket消息
def get_images(ws, client_id, prompt):
    prompt_id = queue_prompt(client_id, prompt)['prompt_id']
    print(f'executing....... prompt_id:{prompt_id}')
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    print('执行完成')
                    break  # 执行完成
        else:
            continue  # 预览为二进制数据

    history = get_history(prompt_id)[prompt_id]
    # print(history)
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        # 图片分支
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output
        # 视频分支
        if 'videos' in node_output:
            videos_output = []
            for video in node_output['videos']:
                video_data = get_image(video['filename'], video['subfolder'], video['type'])
                videos_output.append(video_data)
            output_images[node_id] = videos_output

    print(f'获取图片完成')
    return output_images


# 解析工作流并获取图片
def parse_worflow(ws, client_id, prompt, seed):
    print('workflow_file:' + workflow_file)
    with open(workflow_file, 'r', encoding="utf-8") as workflow_param:
        prompt_data = json.load(workflow_param)

        if os.path.basename(workflow_file) == 'workflow_api.json':
            prompt_data["25"]["inputs"]["noise_seed"] = seed
            prompt_data["70"]["inputs"]["string"] = prompt
        elif os.path.basename(workflow_file) == 'workflow_api_xl.json':
            prompt_data["3"]["inputs"]["seed"] = seed
            prompt_data["13"]["inputs"]["text_positive"] = prompt

        return get_images(ws, client_id, prompt_data)


# 生成图像并显示
def generate_clip(client_id, prompt, seed, start_time, end_time):
    print(f'seed:{str(seed)} client_id:{str(client_id)}')
    ws = websocket.WebSocket()
    paths = []
    try:
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        images = parse_worflow(ws, client_id, prompt, seed)
        paths = []
        for node_id in images:
            for image_data in images[node_id]:
                # 获取当前目录
                file_path = os.path.join(srt_util.get_dir_comfyui_pic(client_id),
                                         generate_img_name(client_id, prompt, start_time, end_time))
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as binary_file:
                    # 写入二进制文件
                    binary_file.write(image_data)
                paths.append(file_path)
        print("{} DONE!!!".format(paths))
    except Exception as e:
        logger.info(e)
    finally:
        ws.close(1000, "Normal Closure")
        return paths


def generate_img_name(client_id, prompt, start_time, end_time):
    return "{}_{}_{}.png".format(utils.md5(prompt), start_time, end_time)


if __name__ == "__main__":
    prompt = """
    Li Ru helps Dong Zhuo after he has been knocked down. They are in a traditional Chinese academy, with wooden furniture and scrolls on the walls. Li Ru assists Dong Zhuo in sitting down, and Dong Zhuo starts to speak. The atmosphere is tense, with soft natural light coming through paper windows.
    """
    client_id = str(uuid.uuid4())  # 生成一个唯一的客户端ID
    # generate_clip(client_id, llm.generate_translate_tip(prompt,
    #                                                     "during the late Western Han Dynasty and the Three Kingdoms period"),
    #               generate_random_seed(),0,0)
    llm.generate_translate_tip(prompt,
                               "during the late Western Han Dynasty and the Three Kingdoms period")

    # idx = 1
    # for prompt in prompts:
    #     seed = generate_random_seed()
    #
    #     idx += 1
