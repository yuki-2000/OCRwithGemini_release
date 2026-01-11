# -*- coding: utf-8 -*-

#https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb?hl=ja#templateParams=%7B%22MODEL_ID%22%3A%20%22gemini-3-pro-preview%22%7D&sandboxMode=true&scrollTo=VTzuBfHyWAg5

#https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb?hl=ja#scrollTo=Generate_JSON

# pip install -q -U google-genai

from google import genai
from google.genai import types
from typing import List, Literal
from pydantic import BaseModel, Field



api_key="YOUR API KEY"
upload_file = "./NASA_sp125_Chapter4.pdf"
json_filename="output.json"
md_filename="output.md"



prompt = """
あなたは高度な文書解析および翻訳の専門AIです。添付されたPDF（画像スキャン）を解析し、以下の指示に従って「1. 図表のJSONリスト」および「2. 日本語翻訳のMarkdownテキスト」の順で出力してください。

### 1. 処理の基本ルール
- **言語**: 英語から日本語へ翻訳してください。
- **読解順序**: ページ内のレイアウト（2段組など）を正確に認識し、人間が読む自然な順序でテキストを抽出してください。
- **欠落の禁止**: 文中のいかなるセクション、段落、一文も省略したり要約したりせず、全文を翻訳してください。
- **除外事項**: ページ番号、ヘッダー、フッターの翻訳・抽出は不要です。

### 2. **図と表の抽出リスト (JSON形式)**
   - 文書内のすべての「図（Figure）」と「表（Table）」を特定してください。
   - 図表番号がなく文章の行内に存在する「図（Figure）」と「表（Table）」も存在するので、すべて特定してください。
   - 各図表の範囲は図表に加え、存在する場合は図表番号（例: Fig. A6.3, Table A5.1）がある部分まで含んでください。
   - 各図表について、切り出すための座標（Bounding Box）を特定してください。
   - 座標はPDFのページサイズに対する相対値として **0から1000の範囲（正規化座標）** で `[ymin, xmin, ymax, xmax]` の順に出力してください。
   - `page_number` は 1 から始まるページ番号です。
   - `filename` は `p1_fig_01.png`, `p5_table_01.png` のように`p[ページ番号]_[fig/table]_[連番].png`命名してください。

### 3. **ドキュメント内容 (Markdown形式)**
   - 本文を日本語に翻訳し、Markdown形式で出力してください。
   - 翻訳する際は以下のルールを必ず守ってください
      ***Markdown形式の維持**: すべてのMarkdownタグ（#、-、1.、>、|、[ ]など）はそのまま維持し、構造を崩さないでください。
      ***全文翻訳**: 文章の一部を省略したり、要約したりせず、すべての内容を正確に翻訳してください。
      ***専門用語**: 技術的な文脈で一般的に英語のまま使われる用語（例：Instance, Deploy, Repositoryなど）は、無理に訳さずカタカナ表記にするか、英語のままにしてください。
      ***トーン**: 自然で丁寧な技術文書のスタイル（だ・である調）で翻訳してください。
   - Markdownのスタイルは以下のルールを守ってください。
      *見出し（#）、箇条書き（-）、太字（**）を適切に使用し、視認性を高めてください。
      *段落の区切りには必ず空行を1行入れてください。
      *改行を行う場合は、行末に半角スペース2つを付与してください。
      *マークダウンファイルの見やすさや、マークダウンタグの範囲を指定するためにも、適切に改行や空行、空白を入れください。
   - 数式はtex形式でインラインもしくはブロック数式で表現し、以下のルールを守ってください。
       *数式はtex形式で$マークを使って表現し、特殊文字と特殊記号は適切にバックスラッシュを使用してください。
       *tex形式のインライン数式を表現する際は、`本文 $\tau$ 本文`というように数式の前後には半角スペースを入れ、`$`と中身の数式コマンドの間には空白文字を絶対に入れないでください。**正しい例**: `$\tau$`、`$x+y=z$‘、**悪い例**: `$ \tau $`、`$ x+y=z $`（これらは絶対に避けてください）
       *tex形式のブロック数式を表現する際は、`本文\n\n$$\n\tau\n$$\n\n本文`というように数式の前後には改行を2つ入れ、数式中の$$で囲まれた数式コマンドの前後には改行を入れて空白文字は入れないでください。
       *空白や改行はtexにおける数式コマンドが適切に機能するように配置してください。
       *数式内の文字の順番は、元のPDFの順番のままで変えないでください。
   - **重要:** 抽出リストで特定した図表がある位置には、対応する画像リンク `![図表の説明](filename)` を挿入してください。summerize this pdf in Japanse"
"""





#json形式の構造化出力に使用
#https://ai.google.dev/gemini-api/docs/structured-output?hl=ja&example=recipe
class FigureTableItem(BaseModel):
    """
    ドキュメント内の図または表の情報を定義するモデル
    """
    id: str = Field(description="図表の一意識別子（例: p1_fig1, p5_tab1）")
    filename: str = Field(description="保存する際のファイル名（例: p1_fig_01.png）")
    page_number: int = Field(description="1から始まるページ番号")
    box_2d: List[int] = Field(
        description="[ymin, xmin, ymax, xmax] の順で、0-1000の範囲で正規化された座標",
        min_items=4,
        max_items=4
    )
    type: Literal["figure", "table"] = Field(description="図(figure)か表(table)かの種別")
    #caption: str = Field(description="図表の説明（キャプション）")
    caption: str = Field(description="本文中の図表の番号（例: Fig. A6.3, Table A5.1）")

class DocumentExtractionResponse(BaseModel):
    """
    Geminiからの最終的なレスポンス形式
    """
    extractions: List[FigureTableItem] = Field(description="抽出された図表のリスト")
    #content_markdown: str = Field(description="図表のリンク（![図表の説明](filename)）を含む、Markdown形式の本文")
    content_markdown: str = Field(description="図表のリンク（![図表の番号](filename)）を含む、Markdown形式の本文")





import json
import os
import re

# markdownでtex数式が適切に出力されるように処理
def fix_inline_math_spaces(text):
    # インライン数式 ($...$) の中身だけを抽出して前後スペースを消す正規表現
    # (?<!\$)  : 前に $ がない（ブロック数式 $$ を避ける）
    # \$       : 開始の $
    # ([^\$]+) : $ 以外の文字（数式の中身）をグループ1としてキャプチャ
    # \$       : 終了の $
    # (?!\$)   : 後ろに $ がない（ブロック数式 $$ を避ける）
    inline_pattern = r'(?<!\$)\$([^\$]+)\$(?!\$)'

    def shrink_match(match):
        # match.group(1) は数式の中身（例: " \tau "）
        # これを strip() して両端の空白を消し、再び $ で囲む
        inner_content = match.group(1).strip()
        return f" ${inner_content}$ "

    # 数式の中身だけをきれいにし、外側のスペースには触れない
    fixed_text = re.sub(inline_pattern, shrink_match, text)
    
    return fixed_text
#このコードのメリット
#外側のスペースを守る: $ $ のペアを見つけてからその「中身」だけを処理するため、本文 $ の間にあるスペースは削除されません。
#ブロック数式を壊さない: $$（ブロック数式）は正規表現の否定条件（(?<!\$)など）によって除外されるため、改行が必要なブロック数式が崩れることはありません。
#複雑な数式に対応: $ x + y = z $ のように中にスペースが含まれる場合も、「両端のスペース」だけを消して $x + y = z$ にしてくれます。






# 保存用
def save_outputs(extraction_data, json_filename="output.json", md_filename="output.md"):
    """
    抽出されたデータをJSONファイルとMarkdownファイルに保存する
    """
    
    # 1. JSONファイルの保存
    # extractions（図表リスト）のみを保存する場合
    extraction_list = [item.model_dump() for item in extraction_data.extractions]
    
    with open(json_filename, "w", encoding="utf-8") as f:
        # ensure_ascii=False を指定することで日本語の文字化けを防ぎます
        json.dump(extraction_list, f, ensure_ascii=False, indent=2)
    
    # 2. Markdownファイルの保存
    with open(md_filename, "w", encoding="utf-8", newline='\n') as f:
        f.write(fix_inline_math_spaces(extraction_data.content_markdown.replace('\\n', '\n'))) #geminiはエスケープして出力することあり

    print(f"保存完了: {json_filename}, {md_filename}")




#--------------------------------------------------------------------------------
#実行



client = genai.Client(api_key=api_key)

file_upload = client.files.upload(file=upload_file)

#apiでサーバーに送信
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[file_upload, prompt],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="low",#"high", #"medium", #"low" <, "minimal"　#low and minimal has no thinking
            include_thoughts=True),
        response_mime_type="application/json",
        response_schema=DocumentExtractionResponse
        )
    )

#返ってきた内容を表示。
for part in response.parts:
  if not part.text:
    continue
  if part.thought:
    print("### Thought summary:")
    print(part.text)
    print()
  else:
    print("### Answer:")
    print(part.text)
    import json
    result = json.loads(part.text)
    print()


# Pythonオブジェクトとして扱う
extraction_data = DocumentExtractionResponse(**result)


# 保存
save_outputs(extraction_data, json_filename, md_filename)



print(f"We used {response.usage_metadata.thoughts_token_count} tokens for the thinking phase and {response.usage_metadata.prompt_token_count} for the output.")

#print(response.text)


print("Prompt tokens:",response.usage_metadata.prompt_token_count)
print("Thoughts tokens:",response.usage_metadata.thoughts_token_count)
print("Output tokens:",response.usage_metadata.candidates_token_count)
print("Total tokens:",response.usage_metadata.total_token_count)


