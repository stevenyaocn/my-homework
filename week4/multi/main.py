# 视觉理解
# import os
# from openai import OpenAI
#
# model = "qwen-vl-max-latest"
# client = OpenAI(
#     api_key=os.getenv("DASHSCOPE_API_KEY"),
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
# )
#
# completion = client.chat.completions.create(
#     model="qwen-vl-max-latest",
#     messages=[
#         {
#             "role": "system",
#             "content": [{"type": "text", "text": "你是一位非常资深的图片鉴别专家"}],
#         },
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://p6.itc.cn/q_70/images03/20200602/0c267a0d3d814c9783659eb956969ba1.jpeg"
#                     },
#                 },
#                 {"type": "text", "text": "图中描绘的是什么景象?"},
#             ],
#         },
#     ],
# )
#
# print(completion.choices[0].message.content)
#
# import os
# import io
# import json
# import base64
# import dashscope
# from IPython.display import display, Markdown
# from PIL import Image
# from dashscope import MultiModalConversation
#
#
# def analyze_image_with_bailian(image_path):
#     """
#     使用阿里云百炼大模型分析图片内容
#     :param image_path: 本地图片路径
#     :return: 分析结果
#     """
#     # 设置API Key
#     dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
#
#     # 根据图片地址，读取图片，并转换为base64
#     def decode_image(path):
#         with open(path, "rb") as f:
#             return base64.b64encode(f.read()).decode("utf-8")
#
#     image_base64 = decode_image(image_path)
#
#     try:
#         # 使用MultiModalConversation调用阿里云百炼大模型
#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"image": f"data:image/jpeg;base64,{image_base64}"},
#                     {"text": "请详细描述这张图片中的内容。"}
#                 ]
#             }
#         ]
#
#         response = MultiModalConversation.call(
#             model="qwen-vl-plus",
#             messages=messages
#         )
#
#         # 返回格式化后的结果
#         if response.status_code == 200:
#             return response.output.choices[0].message.content[0]["text"]
#         else:
#             print(f"请求失败，状态码：{response.status_code}")
#             print(f"错误信息：{response.message}")
#             return None
#
#     except Exception as e:
#         print(f"发生异常：{str(e)}")
#         return None
#
# if __name__ == "__main__":
#
#     # 本地图片路径
#     image_path = "handwriting_1.jpg"
#     result = analyze_image_with_bailian(image_path)
#
#     if result:
#         print("图片内容识别结果：")
#         # print(result)
#         md = display(Markdown(result))
#         print(md)
#     else:
#         print("图片识别失败！")

# 视觉推理
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

reasoning_content = ""
answer_content = ""
is_answer = False

completion = client.chat.completions.create(
    model="qvq-max",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg"}
                },
                {
                    "type": "text",
                    "text": "这道题怎么解？"
                }
            ]
        }
    ],
    stream=True
)

print("\n"+"="*20+"思考过程"+"="*20+"\n")

for chunk in completion:
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
    else:
        detal = chunk.choices[0].delta
        # 打印思考过程
        if hasattr(detal, "reasoning_content") and detal.reasoning_content != None:
            print(detal.reasoning_content, end="", flush=True)
            reasoning_content += detal.reasoning_content
        else:
            # 开始回复
            if detal.content != "" and is_answer is False:
                print("\n"+'='*20+"完整回复"+'='*20+"\n")
                is_answer = True

            print(detal.content, end="", flush=True)
            answer_content += detal.content





























