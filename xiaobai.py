import os
import pycurl
import json
import time
import hmac
import hashlib
import base64
import random
import schedule
import ijson
import openai

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

webhook_url = os.getenv("WEBHOOK_URL")
secret = os.getenv("SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")

item_counts = 0
send_time = "15:04:59"

def get_response(prompt):
    model_engine = "GPT-3.5-turbo"
    prompt = f"{prompt}\n"
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a talented poet."},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "对诗词的解析中请不要照抄诗词本身."},
                {"role": "user", "content": "请你鉴赏一下这首诗, 鉴赏内容以“这首诗”作为开始."}
            ]
    )
    print("completions : ", completions )
    message = completions['choices'][0]['message']['content']
    return message

def get_item_count():
    global item_counts
    with open('result.json', 'r', encoding='utf-8') as f:
        data = ijson.items(f, 'datas.item')
        while True:
            try:
                data.__next__()
                item_counts += 1
            except StopIteration as e:
                print("except item_counts: ", item_counts)
                break

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

def select_poem_random():
    global item_counts
    get_item_count()
    # 打开JSON文件并加载为Python对象
    with open('result.json', 'r', encoding='utf-8') as f:
        data = ijson.items(f, 'datas.item')
        choice_num = random.choice(range(item_counts))
        print("choice_num: ", choice_num)
        loacl_count = 0
        while loacl_count < choice_num:
            data.__next__()
            loacl_count += 1
        while True:
            random_item = data.__next__()
            if random_item["内容"] != "" and random_item["内容"] != [''] \
            and random_item['诗名'] != "" and random_item['诗名'] != ['']:
                break
        prompt = ""
        message = f"**{random_item['诗名']}** \n\n"
        message += f"***{random_item['作者']}*** \n\n"

        for content in random_item["内容"]:
            message += f"**{content}** \n"
            prompt += f"{content}\n"
        message += "\n --------------\n"
        if random_item["出自诗集"]!="" and random_item["出自诗集"]!=['']:
            message += f"*出自诗集：{random_item['出自诗集']}* \n"
        if random_item["章"]!="" and random_item["章"]!=['']:
            message += f"*{random_item['章']}* ."
        if random_item["节"]!="" and random_item["节"]!=['']:
            message += f"*{random_item['节']}* \n"
        if random_item["注"]!="" and random_item["注"]!=['']:
            if isinstance(random_item["注"], str):
                message += f"注：{random_item['注']}\n"
            else:
                message += f"注："
                for content in random_item["注"]:
                    message += f"{content} "
                message += "\n"
        if random_item["解读"]!="" and random_item["解读"]!=['']:
            if isinstance(random_item["解读"], str):
                message += f"解读：{random_item['解读']}\n"
            else:
                message += f"解读："
                for content in random_item["解读"]:
                    message += f"{content} "
                message += "\n"
        else:
            response = get_response(f"{prompt}, 请详细解释这首诗的意思，不需要给出是哪位诗人所作，也不需要给出来自哪部作品")
            message += f"小白解读：{response}"
        print(message)
        return message
    
def send_message():
    # 生成时间戳和签名
    timestamp = str(int(time.time()))
    signature = gen_sign(timestamp, secret)

    # 构造POST请求的数据，根据机器人API文档要求修改
    # 这里可以替换成你要发送的诗歌内容
    poem = select_poem_random()
  
    data = {
        "timestamp": f"{timestamp}",
        "sign": f"{signature}",
        "msg_type": "interactive",
        "card": {
            "elements": [{
                    "tag": "div",
                    "text": {
                            "content": f"{poem}",
                            "tag": "lark_md",
                            "text_align": "center"
                    }
                }],
        "header": {
                "title": {
                        "content": "每日诗词",
                        "tag": "plain_text",
                        "text_align": "center"
                        }
                }
        }
    }

    # 将POST请求数据编码为JSON格式
    post_data = json.dumps(data).encode('utf-8')

    # 初始化 curl 对象
    curl = pycurl.Curl()

    # 设置POST请求的URL和数据
    curl.setopt(curl.URL, webhook_url)
    curl.setopt(curl.POSTFIELDS, post_data)

    # 设置请求头信息，包括时间戳和签=
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    # 执行请求
    curl.perform()
    # 关闭 curl 对象
    curl.close()

# 在指定时间发送一次诗词
schedule.every().day.at(f"{send_time}").do(send_message)

while True:
    schedule.run_pending()
    time.sleep(1)
