import os
import gradio as gr
from pathlib import Path
from week7.sales_chatbot.core import ChatEngine


class GradioUI:
    def __init__(self):
        self.chat_engine = ChatEngine()
        self.categories = ["电器", "家装", "房产"]
        self.file_types = ["txt", "pdf", "docx"]  # 支持的文件类型

    def create_interface(self):
        with gr.Blocks(title="AI知识助手") as demo:
            # 使用State存储对话历史
            chat_history = gr.State([])

            with gr.Tab("知识库管理"):
                with gr.Row():
                    file_input = gr.File(label="上传知识文档", type="filepath")
                with gr.Row():
                    category_select = gr.Dropdown(
                        label="知识库类型",
                        choices=self.categories
                    )

                upload_btn = gr.Button("上传并构建索引")
                upload_status = gr.Markdown()

                # 添加上传回调
                upload_btn.click(
                    self._upload_knowledge,
                    inputs=[file_input, category_select],
                    outputs=upload_status
                )

            with gr.Tab("智能咨询"):
                chatbot = gr.Chatbot(height=500)
                q_category = gr.Dropdown(
                    label="问题类型",
                    choices=self.categories
                )
                msg = gr.Textbox(label="输入问题")
                submit_btn = gr.Button("提交")

            upload_btn.click(
                fn=self._upload_knowledge,
                inputs=[file_input, category_select],
                outputs=upload_status
            )

            submit_btn.click(
                fn=self._chat_response,
                inputs=[msg, q_category, chat_history],
                outputs=[chatbot, chat_history]
            ).then(
                lambda: "",  # 返回空字符串
                inputs=None,
                outputs=msg  # 明确指定输出组件
            )
        return demo

    def _upload_knowledge(self, file_path: str, category: str):
        try:
            if not os.path.exists(file_path):
                return "❌ 文件不存在"

            # print(f"开始上传知识库文件")
            file_type = Path(file_path).suffix
            if file_type:
                file_type = file_type[1:] # 去掉第一个字符（点）
                # print(f"上传的知识库文件类型：{file_type}")

            if file_type not in self.file_types:
                return f"❌ 不支持的文件类型: {file_type}"

            return self.chat_engine.upload_knowledge(
                file_path=file_path,
                file_type=file_type,
                knowledge_type=category
            )
        except Exception as e:
            return f"❌ 上传失败: {str(e)}"

    def _chat_response(self, message: str, category: str, chat_history: list) -> tuple:
        """Gradio对话回调"""
        # print(f"问题：{message}，类别：{category}，历史聊天记录：{chat_history}")

        """处理对话响应"""
        if not message.strip():
            return chat_history, chat_history  # 忽略空消息
        try:
            response = self.chat_engine.get_response(
                query=message,
                category=category,
                history=chat_history
            )

            # print(f"AI调用知识库/联网检索结果：{response}")

            # 更新对话历史（限制长度）
            new_history = chat_history + [(f"问题类型：{category}\n\n{message}", response)]
            trimmed_history = new_history[-self.chat_engine.max_history_length:]
            # print(f"限制历史长度后返回结果：{trimmed_history}")

            return trimmed_history, new_history
        except Exception as e:
            error_msg = f"对话出错: {str(e)}"
            return chat_history + [(message, error_msg)], chat_history