# import json
# import os
#
# import dashscope
# from http import HTTPStatus
#
# painting_assistant = dashscope.Assistants.create(
#     api_key=os.getenv("DASHSCOPE_API_KEY"),
#     model="qwen-max",
#     name="Art Maestro艺术大师",
#     description="一个专注于绘画和艺术知识的AI助手",
#     instructions="你是一个专家级的绘画助手，并在需要的时候利用图像生成工具创建视觉示例...",
#     tools=[
#         {"type": "quark_search", "description": "使用此工具查找关于绘画技巧、艺术史和艺术家的详细信息"},
#         {"type": "text_to_image", "description": "使用此工具创建绘画风格、技巧或艺术概念的视觉示例"}
#     ]
# )
# print(f"绘画助手 Art Maestro艺术大师 创建成功，ID:{painting_assistant.id}")
#
# thread = dashscope.Threads.create()
# if thread.status_code == HTTPStatus.OK:
#     print(f"线程创建成功。线程ID:{thread.id}")
# else:
#     print(f"线程创建失败！状态码：{thread.status_code}")
#
# message = dashscope.Messages.create(thread_id=thread.id, content="请帮我画一幅清明上河图卡通画。")
# if message.status_code == HTTPStatus.OK:
#     print(f"消息创建成功。消息ID: {message.id}")
# else:
#     print(f"消息创建失败！状态码：{message.status_code}")
#
# run = dashscope.Runs.create(thread_id=thread.id, assistant_id=painting_assistant.id)
# if run.status_code == HTTPStatus.OK:
#     print(f"创建助手成功。助手ID:{run.id}")
# else:
#     print(f"创建助手失败！错误码：{run.status_code} ##错误消息：{run.status_code}")
#
# run = dashscope.Runs.wait(run_id=run.id, thread_id=thread.id)
# if run.status_code == HTTPStatus.OK:
#     print(run)
# else:
#     print(f"获取助手运行失败！状态码：{run.status_code}")
#
# msgs = dashscope.Messages.list(thread_id=thread.id)
# if msgs.status_code == HTTPStatus.OK:
#     print(json.dumps(msgs, default=lambda o:o.__dict__, sort_keys=True, indent=4))
# else:
#     print(f"获取消息失败！状态码：{msgs.status_code}")
# import os
#
# from dashscope import (Assistants, Threads, Messages, Runs, Steps)
#
#
# def init_assistant() -> str:
#     assistant = Assistants.create(
#         api_key=os.getenv("DASHSCOPE_API_KEY"),
#         model="qwen-plus",
#         name="Chat Assistant",
#         instructions="You are a helpful assistant",
#         metadata={"env": "test"}
#     )
#     print(f"Assistant was created successfully! Assistant ID: {assistant.id}")
#     return assistant.id
#
#
# def start_session(assistant_id: str, user_input: str) -> str:
#     thread = Threads.create(
#         metadata={"session_owner": "User123456"}
#     )
#
#     Messages.create(
#         thread_id=thread.id,
#         content=user_input,
#         role="user"
#     )
#
#     print(f"Thread was created successfully! Thread ID: {thread.id}")
#     return thread.id
#
#
# def get_assistant_reply(assistant_id: str, thread_id: str) -> str:
#     run = Runs.create(
#         thread_id=thread_id,
#         assistant_id=assistant_id,
#         model="qwen-plus"
#     )
#
#     final_run = Runs.wait(
#         run_id=run.id,
#         thread_id=thread_id,
#         timeout_seconds=60
#     )
#
#     thread_messages = Messages.list(
#         thread_id=thread_id
#     )
#
#     if thread_messages.data:
#         last_msg = thread_messages.data[0]
#         return last_msg
#
#     return "No reply."
#
#
# def end_session(thread_id: str):
#     Threads.delete(thread_id=thread_id)
#
# assistant_id = init_assistant()
#
# print("Please input your chat message! if you want to exit, please input 'exit'")
# while True:
#     user_input = input("Chat Message:")
#     if user_input == "exit":
#         break;
#     thread_id = start_session(
#         assistant_id=assistant_id,
#         user_input=user_input
#     )
#     reply = get_assistant_reply(assistant_id=assistant_id,thread_id=thread_id)
#     print(f"Assistant reply: {reply}")
#
# end_session(thread_id=thread_id)

from dashscope import Assistants, Threads, Runs


def main():
    # 创建支持代码解释器的Assistant
    # tools列表中添加code_interpreter使Assistant能够执行Python代码
    assistant = Assistants.create(
        model='qwen-plus',  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        name='简单助手',
        instructions='you are a helpful assistant',
        tools=[{
            'type': 'code_interpreter',
        }]
    )

    # 创建对话线程，请求绘制函数图像
    # 这里要求Assistant思考如何绘图，它会使用code_interpreter来完成任务
    thread = Threads.create(
        messages=[{
            'role': 'user',
            'content': '你好啊，帮我画一幅y=x**2的图像，请你先想想怎么画'
        }])

    # 启动流式对话，设置stream=True来获取实时响应
    run_iterator = Runs.create(
        thread.id,
        assistant_id=assistant.id,
        stream=True
    )

    try:
        # 处理不同类型的流式响应事件
        for event, data in run_iterator:
            # 当一个步骤完成时打印换行
            if event == 'thread.run.step.completed':
                print("\n")
            # 处理Assistant的文本消息
            if event == 'thread.message.delta':
                print(data.delta.content.text.value, end='', flush=True)
            # 处理代码解释器的输出
            if event == 'thread.run.step.delta':
                tool_call = data.delta.step_details.tool_calls[0]
                if getattr(tool_call, 'type', '') == 'code_interpreter':
                    # 打印代码和执行结果
                    print(getattr(tool_call.code_interpreter, 'arguments', ''), end='', flush=True)
                    print(getattr(tool_call.code_interpreter, 'output', ''), end='', flush=True)

    # 异常处理：支持用户中断和错误处理
    except KeyboardInterrupt:
        run_iterator.close()
        print("\n输出被用户中断")
    except Exception as e:
        print(f"\n遇到错误了：{str(e)}")
        run_iterator.close()


if __name__ == '__main__':
    main()
