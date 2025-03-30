import os
import re
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    Image,
    PageBreak,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from openai import OpenAI
import uuid

# 注册中文字体
pdfmetrics.registerFont(TTFont('SimSun', '../fonts/simsun.ttc'))

# 创建自定义样式
styles = getSampleStyleSheet()
simsun_style = ParagraphStyle(
    'SimSun',
    parent=styles['Normal'],
    fontName='SimSun',
    fontSize=12,
    leading=14,
    spaceBefore=6,
    spaceAfter=6
)

model = "qwen-plus"
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)


def extract_images(page):
    """使用pdfplumber提取当前页所有图片，并处理不同图像格式"""
    images = []
    for img in page.images:
        try:
            bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
            cropped_page = page.crop(bbox)
            im = cropped_page.to_image(antialias=True)
            img_path=f"temps/{uuid.uuid4().hex[:8]}.png"
            im.save(img_path)
            images.append({
                "path": img_path,  # 实际文件路径
                "width": img["x1"] - img["x0"],  # 根据原始坐标计算宽度
                "height": img["y1"] - img["y0"],  # 根据原始坐标计算高度
                "x0": img["x0"],  # 原始坐标（可选）
                "y0": page.height - img["y1"]  # 转换为左下角坐标系（可选）
            })
        except Exception as e:
            print(f"图片提取失败：{str(e)}")
    return images


def extract_text_ignore_tables(page):
    """通过替换方式删除文本中的表格内容"""
    # 提取原始文本和表格数据
    text = page.extract_text(x_tolerance=3, y_tolerance=3)
    print(f"提取的原始文本：{text}")
    tables = page.extract_tables()

    # 提取表格行文本并构建正则模式
    table_lines = []
    for table in tables:
        for row in table:
            row_text = " ".join([str(cell).strip() for cell in row if cell])
            if row_text:
                row_text = re.sub(r"\s+", " ", row_text)
                table_lines.append(re.escape(row_text))

    if not table_lines:
        return text

    # 构建正则表达式（支持跨行和多余空格）
    pattern = r"(?:\n\s*|\A\s*)(" + "|".join(table_lines) + r")(?:\s*\n|\s*\Z)"

    # 执行替换
    filtered_text = re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)
    # 二次检查，确保没有遗漏
    for table in tables:
        for row in table:
            row_text = " ".join([str(cell).strip() for cell in row if cell])
            if row_text:
                row_text = re.sub(r"\s+", " ", row_text)
                filtered_text = re.sub(re.escape(row_text), "", filtered_text, flags=re.MULTILINE | re.DOTALL)
    # 执行替换
    return filtered_text.strip()


def translate_text(text, target_language: str = "中文"):
    """增强型翻译函数"""
    if not text.strip():
        return ""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"你是一位{target_language}翻译专家"},
            {"role": "user", "content": f"严格遵循以下规则翻译：\n"
                                        f"1. 保留所有数字、符号和格式\n"
                                        f"2. 表格内容逐单元格翻译\n"
                                        f"3. 不要添加额外内容\n"
                                        f"请将需要翻译的内容翻译成{target_language}，需要翻译的内容：\n{text}"
            }],
        temperature=0.05
    )
    return response.choices[0].message.content.strip()


def process_page(page, page_num, targe_language):
    """处理单页内容"""
    elements = []

    # 提取并存储图片
    images = extract_images(page)

    # 处理文本内容
    # text = page.extract_text(x_tolerance=3, y_tolerance=3)

    text = extract_text_ignore_tables(page)
    print(f"过滤表格之后的文本：{text}")

    if text:
        translated = translate_text(text, targe_language)
        print(f"翻译后的文本内容：{translated}")
        for paragraph in translated.split('\n'):
            if paragraph.strip():
                p = Paragraph(paragraph.replace(' ', '&nbsp;'), simsun_style)
                elements.append(p)
                elements.append(Spacer(1, 12))

    # 处理表格
    tables = page.extract_tables()

    for table in tables:
        translated_table = [
            [Paragraph(translate_text(cell, targe_language).replace(' ', '&nbsp;'), simsun_style)
             if cell else "" for cell in row
             ] for row in table
        ]

        # 创建新表格
        tbl = Table(
            translated_table,
            style=[
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
        )
        elements.append(Spacer(1, 24))
        elements.append(tbl)
        elements.append(Spacer(1, 36))

    # 插入图片（按原始位置排序）
    for img in images:
        elements.append(Image(
            img["path"],
            width=img["width"],
            height=img["height"],
            kind='proportional'
        ))
        elements.append(Spacer(1, 24))

    return elements


def process_pdf(input_pdf, output_pdf, target_language):
    """主处理流程"""
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter
    )

    story = []

    with pdfplumber.open(input_pdf) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            story.extend(process_page(page, page_num, targe_language=target_language))
            if page_num < len(pdf.pages):
                story.append(PageBreak())

    doc.build(story)
    return output_pdf


class PDFTranslator:
    def __init__(self):
        pass

    def translate_pdf(self, pdf_file_path: str, target_language: str = "中文", output_file_path: str = None) -> str:
       return process_pdf(pdf_file_path, output_file_path, target_language)

# # 使用示例
# if __name__ == "__main__":
#     input_pdf = "test.pdf"
#     output_pdf = f"files/translated_{uuid.uuid4().hex[:8]}.pdf"
#     result_path = process_pdf(input_pdf, output_pdf, "日语")
#     print(f"生成文件：file://{os.path.abspath(result_path)}")