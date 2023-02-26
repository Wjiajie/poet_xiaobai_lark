# process poetry datas fetch from https://github.com/chinese-poetry/chinese-poetry
import os
import json
from opencc import OpenCC

glob_dirs = ["caocaoshiji", "ci", "json", "nalanxingde", "shijing", "shuimotangshi", "huajianji","nantang"]

black_lists = ["error", "表面结构字","authors","author", "intro", "preface", "strains"]

name_intro_map = {"author":"作者","title":"诗名","paragraphs":"内容","rhythmic":"出自诗集","tags":"出自诗集",
                  "notes":"注", "para":"内容","chapter":"章","section":"节","content":"内容","prologue":"解读"}

data_folder = "datasets\chinese-poetry"

result = []  # 用于存储解析后的JSON数据

# 创建 OpenCC 转换器
converter = OpenCC('t2s')  # convert from Traditional Chinese to Simplified Chinese

def process_json_data(file_name, json_data):
    # 将新的item添加到一个新的列表中
    new_data = []
    for item in json_data:
        # 创建一个新的item
        new_item = {
            "作者": "",
            "诗名": "",
            "内容": "",
            "出自诗集": "",
            "章": "",
            "节": "",
            "注": "",
            "解读": "",
        }
        if "caocao" in file_name:
            new_item["作者"] = "曹操"
        for key, value in item.items():
            if key in name_intro_map.keys():
                new_item[name_intro_map[key]] = value
        # 繁体字换简体字
        for key, value in new_item.items():
            if isinstance(value, str):
                new_item[key] = converter.convert(new_item[key])
            else:
                for i, paragraph in enumerate(new_item[key]):
                    new_item[key][i] = converter.convert(paragraph)
        result.append(new_item)
                
# 遍历文件夹中的所有子文件夹和文件
for subdir, dirs, files in os.walk(data_folder): 
    for file in files:
        # 仅处理.json文件
        if file.endswith('.json'):
            # 打开文件并解析JSON数据
            if(subdir.split("\\")[-1] in glob_dirs):
                all_pass = True
                for bl in black_lists:
                    if bl in subdir or bl in file:
                        all_pass = False
                if not all_pass:
                    continue

                file_path = os.path.join(subdir, file)
                print(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    process_json_data(file, json_data)

with open('result.json', 'w', encoding='utf-8') as f:
    json.dump({"datas":result}, f, ensure_ascii=False, indent=0)

