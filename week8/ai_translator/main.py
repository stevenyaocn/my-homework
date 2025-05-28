import gradio as gr
import os
import uuid
from translators import PDFTranslator

# 临时文件目录
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def translate_pdf(
        file_obj: gr.File,
        source_lang: str,
        target_lang: str
):
    """
    将上传的PDF翻译成目标语言，返回翻译后的结果下载地址
    :param file_obj: 要翻译的附件
    :param source_lang: 源语言
    :param target_lang: 要翻译的目标语言
    :return: 
    """""

    try:
        validation_errors = []
        if not file_obj:
            validation_errors.append(f"请选择您要翻译的文件！")
        elif os.path.isdir(file_obj):
            validation_errors.append(f"无效的文件路径：{file_obj}不是有效的文件路径。")
        elif not os.path.exists(file_obj):
            validation_errors.append(f"该文件：{file_obj}不存在！")
        else:
            try:
                with open(file_obj, "r") as f:
                    pass
            except PermissionError:
                validation_errors.append(f"无权限访问该文件：{file_obj}")

        if validation_errors:
            error_message = "\n".join(validation_errors)
            print(f"文件翻译失败！失败原因：{error_message}")
            return None

        # 执行文件处理（含翻译文件操作）
        translator = PDFTranslator()
        # 生成唯一文件名
        translated_path = f"files/translated_{uuid.uuid4().hex[:8]}.pdf"
        translator.translate_pdf(pdf_file_path=file_obj, source_language=source_lang, target_language=target_lang, output_file_path=translated_path)

        return gr.File(value=translated_path, visible=True)

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return None


# 创建Gradio界面
with gr.Blocks(title="AI Translator v2.0") as app:
    gr.Markdown("# 📄 AI Translator v2.0（PDF电子书翻译工具）")

    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传PDF文件", file_types=[".pdf"])
        with gr.Column():
            # 生成后的附件下载
            download_component = gr.File(visible=True)
    with gr.Row():
        with gr.Column():
            source_lang = gr.Textbox(label="源语言（默认：英文）", placeholder="English")
            target_lang = gr.Textbox(label="目标语言（默认：中文）", placeholder="Chinese")
        with gr.Column():
            pass
    with gr.Row():
        with gr.Column():
            submit_btn = gr.Button("Submit", variant="primary")
        with gr.Column():
            pass

    submit_btn.click(
        fn=translate_pdf,
        inputs=[file_input, source_lang, target_lang],
        outputs=[download_component]
    )

# 启动应用
if __name__ == "__main__":
    app.launch(server_port=8080)