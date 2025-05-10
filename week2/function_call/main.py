from datetime import datetime
import os
import requests
import json
from openai import OpenAI

LBS_MAP_KEY = os.getenv("LBS_MAP_KEY")
model = "qwen-plus"
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# prompt = "今天苏州天气怎么样？"
#
# def get_completion(prompt, model="qwen-plus"):
#     message = [
#         {"role": "system", "content": "你是一位天气预报专家"},
#         {"role": "user", "content": prompt}
#     ]
#
#     response = client.chat.completions.create(
#         model=model,
#         messages=message
#     )
#
#     return response.choices[0].message.content
#
# print(get_completion(prompt))

def get_current_weather(city):
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?key={LBS_MAP_KEY}&city={city}"
    response = requests.get(
        url=url,
        timeout=10
    )
    print(response.text)
    return response.text
    # result = eval(response.text)["lives"][0]
    # weather_info = {
    #     "city": city,
    #     "weather": result["weather"],
    #     "temperature": result["temperature"],
    #     "time": result["reporttime"]
    # }
    # return json.dumps(weather_info, ensure_ascii=False)
#
# get_current_weather("苏州")

city = input("请输入您要查询天气预报的城市：")

messages = []
messages.append({"role": "system", "content": "你是一位天气预报专家，根据用户提供的城市信息回答当天该城市的天气情况"})
messages.append({"role": "user", "content": f"""今天{city}的天气怎么样？"""})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    # 查询天气时需要提供位置，因此参数设置为location
                    "city": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                }
            },
            "required": [
                "city"
            ]
        }
    }
]

response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools
)

function_message = response.choices[0].message
print(type(function_message),function_message)
messages.append(function_message)
# print(messages)

function_name = response.choices[0].message.tool_calls[0].function.name
# print(function_name)

function_id = response.choices[0].message.tool_calls[0].id
# print(function_id)

messages.append({
    "tool_call_id": function_id,
    "role": "tool",
    "name": function_name,
    "content": get_current_weather(city)
})

# print(messages)

response = client.chat.completions.create(
    model=model,
    messages=messages
)

print(response.choices[0].message.content)