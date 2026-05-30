# clean_md.py
import sys
import re

def clean_markdown_for_epub(content):
    """
    Markdownファイル内の数式などをPandoc/MathML/EPUB向けに
    自動的かつ安全に補正・クリーニングする関数
    """
    # 1. インチ記号の補正。
    #    \text{...} の中にある " は LaTeX/texmath で正常に扱えるので温存する。
    #    数式中で \text{} の外に裸で出ている " だけを、テキストとして安全な
    #    ダブルプライム ″ (U+2033) に置換する。\text{''} への置換はネストを
    #    生んで Pandoc を落とすため使わない。
    #
    #    仕組み: \text{...}（1段ネストまで許容）を選択肢の左側に置いて先に
    #    丸ごと消費させ、その外側にある裸の " だけが repl で置換される。
    _text_or_quote = re.compile(r'\\text\{(?:[^{}]|\{[^{}]*\})*\}|"')

    def _fix_quotes(math_part):
        def repl(m):
            s = m.group(0)
            if s == '"':
                return '″'   # \text{} の外の裸のインチ記号
            return s         # \text{...} はそのまま温存
        return _text_or_quote.sub(repl, math_part)

    # $$ ... $$ (ブロック数式) と $ ... $ (インライン数式) の中だけに適用
    content = re.sub(r'\$\$.*?\$\$', lambda m: _fix_quotes(m.group(0)), content, flags=re.DOTALL)
    content = re.sub(r'\$.*?\$', lambda m: _fix_quotes(m.group(0)), content)

    # 2. \tag{...} を数式ブロックの外側に自動で退避させる
    def process_block(match):
        block_content = match.group(1)
        tag_match = re.search(r'\\tag\{([^}]+)\}', block_content)
        if tag_match:
            tag_val = tag_match.group(1)
            cleaned_block = re.sub(r'\\tag\{[^}]+\}', '', block_content).strip()
            return f"$$\n{cleaned_block}\n$$\n*({tag_val})*"
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