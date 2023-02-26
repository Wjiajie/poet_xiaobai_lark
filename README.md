# poet_xiaobai_lark
A Lark robot that pushes poetry at a fixed point every day



### install

* clone repo

```python
git clone git@github.com:Wjiajie/poet_xiaobai_lark.git

```

* see `datasets\README.md` to download datasets

* run

```python
pip3 install opencc
python pre_process.py
```

to generate post-process datasets.

* config your lark robot WEBHOOK_URL and SECRET at `.env` file, see [自定义机器人指南 - 客户端文档 - 开发文档 - 飞书开放平台 (feishu.cn)](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN).
* config your openai-api key at `.env` file, see [OpenAI API](https://openai.com/api/).
* run

```python
pip3 install pycurl ijson openai python-dotenv
python xiaobai.py
```



