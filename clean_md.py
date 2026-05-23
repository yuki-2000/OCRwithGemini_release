# clean_md.py
import sys
import re

def clean_markdown_for_epub(content):
    """
    Markdownファイル内の数式などをPandoc/MathML/EPUB向けに
    自動的かつ安全に補正・クリーニングする関数
    """
    # 1. インチ記号 (") を LaTeX で正当な表現 (\text{''}) に置換
    def replace_in_math(match):
        math_part = match.group(0)
        fixed_math = math_part.replace('"', r"\text{''}")
        return fixed_math

    content = re.sub(r'\$\$.*?\$\$', replace_in_math, content, flags=re.DOTALL)
    content = re.sub(r'\$.*?\$', replace_in_math, content)

    # 2. \tag{...} を数式ブロックの外側に自動で退避させる
    def process_block(match):
        block_content = match.group(1)
        tag_match = re.search(r'\\tag\{([^}]+)\}', block_content)
        if tag_match:
            tag_val = tag_match.group(1)
            cleaned_block = re.sub(r'\\tag\{[^}]+\}', '', block_content).strip()
            return f"$$\n{cleaned_block}\n$$\n*(式 {tag_val})*"
        return match.group(0)

    content = re.sub(r'\$\$(.*?)\$\$', process_block, content, flags=re.DOTALL)

    # 3. インライン数式のスペース補正 (エスケープされたドルマーク \$ を壊さない版)
    inline_pattern = r'(?<!\\)(?<!\$)\$([^\$]+)(?<!\\)\$(?!\$)'
    def shrink_match(match):
        inner_content = match.group(1).strip()
        return f" ${inner_content}$ "
    
    content = re.sub(inline_pattern, shrink_match, content)

    # 4. 結合用特殊Unicode（U+0300〜U+036F）を一括削除
    content = re.sub(r'[\u0300-\u036f]', '', content)

    return content


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python clean_md.py <input_file_path> <output_file_path>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # 1. 元ファイルを読み込む（上書きしません）
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    cleaned = clean_markdown_for_epub(raw_content)

    # 2. 別途指定された一時ファイルのパスに書き出す
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(cleaned)
    print(f"Successfully cleaned '{input_path}' and saved to temp file: '{output_path}'")