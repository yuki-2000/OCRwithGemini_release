import fitz  # PyMuPDF
import json
import os

def crop_images_from_pdf(pdf_path, json_path, output_dir="./", padding_ratio=0.05):
    """
    JSONの座標をもとに、指定割合(padding_ratio)だけ広い範囲を切り出す
    padding_ratio=0.05 は、上下左右にそれぞれ5%広げ（計10%拡大）ることを意味します。
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        extractions = json.load(f)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)

    for item in extractions:
        page_num = item['page_number'] - 1
        filename = item['filename']
        ymin, xmin, ymax, xmax = item['box_2d']

        # 1. 元のサイズを計算
        width = xmax - xmin
        height = ymax - ymin

        # 2. 範囲を広げる (上下左右に指定割合ずつ)
        # 左右に width * 0.05 ずつ、上下に height * 0.05 ずつ広げる
        xmin_new = xmin - (width * padding_ratio)
        xmax_new = xmax + (width * padding_ratio)
        ymin_new = ymin - (height * padding_ratio)
        ymax_new = ymax + (height * padding_ratio)

        # 3. 0〜1000の範囲内に収まるように補正 (ページ外はみ出し防止)
        xmin_new = max(0, xmin_new)
        ymin_new = max(0, ymin_new)
        xmax_new = min(1000, xmax_new)
        ymax_new = min(1000, ymax_new)

        # 4. PDFの実際の座標に変換
        page = doc.load_page(page_num)
        p_width = page.rect.width
        p_height = page.rect.height

        left = (xmin_new / 1000) * p_width
        top = (ymin_new / 1000) * p_height
        right = (xmax_new / 1000) * p_width
        bottom = (ymax_new / 1000) * p_height

        rect = fitz.Rect(left, top, right, bottom)

        # 5. 保存 (高画質設定)
        zoom = 3.0 
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, clip=rect)

        output_path = os.path.join(output_dir, filename)
        pix.save(output_path)
        print(f"Saved: {output_path} (Expanded 10%)")

    doc.close()

# 実行
pdf_file = "./NASA_sp125_Chapter4.pdf"
json_file = "output.json"
crop_images_from_pdf(pdf_file, json_file)