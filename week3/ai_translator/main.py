import os
import uuid
import gradio as gr
from typing import List, Tuple
from translator import PDFTranslator

def translate(
    file_path: str,
    model: str,
    target_language: str,
    chat_history: List[Tuple[str, str]]
):

    # 组装用户操作记录
    user_actions = []
    if file_path:
        user_actions.append(f"上传待翻译的文件是：{os.path.basename(file_path)}")
    if model:
        user_actions.append(f"选择的大模型是：{model}")
    if target_language:
        user_actions.append(f"选择要翻译的目标语言是：{target_language}")

    full_query = "\n".join(user_actions) if user_actions else "空操作"

    # 数据严重，如果严重不通过，就不需要执行后面的文件翻译操作
    validation_errors = []

    if not file_path:
        validation_errors.append(f"请选择您要翻译的文件！")
    elif os.path.isdir(file_path):
        validation_errors.append(f"错误的路径类型：{file_path}是目录")
    elif not os.path.exists(file_path):
        validation_errors.append(f"待翻译的文件不存在：{file_path}")
    else:
        try:
            with open(file_path, "r") as f:
                pass
        except PermissionError:
            validation_errors.append(f"无权限访问该文件：{file_path}")

    if not model.strip():
        validation_errors.append(f"请选择AI大模型！")
    if not target_language.strip():
        validation_errors.append(f"请选择您要翻译的目标语言！")

    # 存在验证错误
    if validation_errors:
        error_message = "\n".join(validation_errors)
        chat_history.append((full_query, error_message))
        return chat_history, None

    # 文件是否存在验证，防止上传的临时文件失效
    if not os.path.exists(file_path):
        chat_history.append((full_query, f"您上传的文件已失效，请重新上传。"))
        return chat_history, None

    # 执行文件处理（含翻译文件操作）
    translator = PDFTranslator()
    translated_path = f"files/translated_{uuid.uuid4().hex[:8]}.pdf"
    translator.translate_pdf(pdf_file_path=file_path, target_language=target_language,output_file_path=translated_path)

    # 构建完整回复
    response = f"""文件翻译完成，点击以下链接可以下载翻译好的文件。"""
    chat_history.append((full_query, response))

    print(chat_history)

    return chat_history, gr.File(value=translated_path, visible=True)

# 使用Gradio组件，构建聊天机器人界面
with gr.Blocks(title = "智能文件翻译助手") as ui:
    gr.Markdown("## 智能文件翻译助手")

    file_state = gr.State()
    translated_file = gr.State()

    # 聊天机器人主界面
    chatbot = gr.Chatbot(
        label="翻译对话记录",
        bubble_full_width=False,
        height=400,
        value=[(None,"欢迎使用智能文件翻译助手！请按以下步骤操作：\n1. 上传需要翻译的文件\n2. 选择大模型\n3. 选择您要翻译的目标语言\n4. 点击“开始翻译”按钮执行翻译")]
    )

    # 生成后的附件下载
    download_component = gr.File(visible=False)

    with gr.Row():
        with gr.Column(scale=2):
            # 文件上传组件，选择要翻译的文件
            file_input = gr.File(
                label="上传附件",
                file_types=[".pdf"]
            )
        with gr.Column(scale=3):
            # 模型选择组件
            model_selector = gr.Dropdown(
                label="选择AI大模型",
                choices=["qwen-plus", "deepseek-chat"],
                value="qwen-plus"
            )
            # 需要翻译的目标语言
            target_language_selector = gr.Dropdown(
                label="选择翻译目标语言",
                choices=["英语", "中文", "日语", "德语", "法语"],
                value="英语"
            )
            # 提交按钮
            submit_btn = gr.Button("开始翻译", variant="primary")

    # 事件处理
    file_input.change(
        fn=lambda x: x,
        inputs=file_input,
        outputs=file_state
    )

    submit_btn.click(
        fn=translate,
        inputs=[file_input, model_selector, target_language_selector, chatbot],
        outputs=[chatbot, download_component]
    )

# 启动界面
if __name__ == "__main__":
    ui.launch(server_port=8080)