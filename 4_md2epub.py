# -*- coding: utf-8 -*-

import pypandoc
import os
import re




def clean_markdown_for_epub(content):
    """
    Markdownファイル内の数式などをPandoc/MathML/EPUB向けに
    自動的かつ安全に補正・クリーニングする関数
    """
    # ---------------------------------------------------------
    # 1. インチ記号の補正。
    #    \text{...} の中にある " は LaTeX/texmath で正常に扱えるので温存する。
    #    数式中で \text{} の外に裸で出ている " だけを、テキストとして安全な
    #    ダブルプライム ″ (U+2033) に置換する。\text{''} への置換はネストを
    #    生んで Pandoc を落とすため使わない。
    #
    #    仕組み: \text{...}（1段ネストまで許容）を選択肢の左側に置いて先に
    #    丸ごと消費させ、その外側にある裸の " だけが repl で置換される。
    # ---------------------------------------------------------
    _text_or_quote = re.compile(r'\\text\{(?:[^{}]|\{[^{}]*\})*\}|"')

    def _fix_quotes(math_part):
        def repl(m):
            s = m.group(0)
            if s == '"':
                return '″'   # \text{} の外の裸のインチ記号
            return s         # \text{...} はそのまま温存
        return _text_or_quote.sub(repl, math_part)

    # $$ ... $$ (ブロック数式) と $ ... $ (インライン数式) の中だけに適用
    content = re.sub(r'\$\$.*?\$\$', lambda m: _fix_quotes(m.group(0)),
                     content, flags=re.DOTALL)
    content = re.sub(r'\$.*?\$', lambda m: _fix_quotes(m.group(0)), content)



    # ---------------------------------------------------------
    # 2. \tag{...} を数式ブロックの外側に自動で退避させる
    # ---------------------------------------------------------
    def process_block(match):
        block_content = match.group(1)
        # ブロック内に \tag{...} があるか探す
        tag_match = re.search(r'\\tag\{([^}]+)\}', block_content)
        if tag_match:
            tag_val = tag_match.group(1)
            # \tag{...} の部分を数式ブロック内からきれいに消去
            cleaned_block = re.sub(r'\\tag\{[^}]+\}', '', block_content).strip()
            # 数式ブロックの直後に *(式 4-1)* などの形で式番号を外だしして再構築
            # (前後にしっかり改行を挟むことで、Pandocが別ブロックとして認識できるようにします)
            return f"$$\n{cleaned_block}\n$$\n*({tag_val})*"
        return match.group(0)

    # すべてのブロック数式 $$ ... $$ に対して処理を実行
    content = re.sub(r'\$\$(.*?)\$\$', process_block, content, flags=re.DOTALL)


    # ---------------------------------------------------------
    # 3. インライン数式のスペース補正 (エスケープされたドルマーク \$ を壊さない版)
    # ---------------------------------------------------------
    inline_pattern = r'(?<!\\)(?<!\$)\$([^\$]+)(?<!\\)\$(?!\$)'
    def shrink_match(match):
        inner_content = match.group(1).strip()
        return f" ${inner_content}$ "
    
    content = re.sub(inline_pattern, shrink_match, content)


    # ---------------------------------------------------------
    # 4. KaTeX/MathJaxを壊す原因になる結合用特殊Unicode（U+0300〜U+036F）を一括削除
    # ---------------------------------------------------------
    content = re.sub(r'[\u0300-\u036f]', '', content)

    return content



def convert_md_to_epub():
    input_file = 'output.md'
    output_file = 'output_local.epub'
    title = os.path.splitext(os.path.basename(input_file))[0]

    # 1. 元のMarkdownファイルの存在チェック
    if not os.path.exists(input_file):
        print(f"Error: 入力ファイル '{input_file}' が見つかりません。")
        return

    # 一時ファイルのパスを作成（画像パスの維持のため、入力ファイルと同じディレクトリに配置します）
    input_dir = os.path.dirname(input_file) or '.'
    input_base = os.path.basename(input_file)
    temp_file = os.path.join(input_dir, f"_temp_{input_base}")

    try:
        # 2. 元ファイルを読み込み、自動クリーニングして「一時ファイル」に書き出す
        print("Markdownファイルを読み込んで、自動補正を適用中...")
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        cleaned_content = clean_markdown_for_epub(raw_content)

        # 一時ファイルとして書き出す
        with open(temp_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned_content)
        print(f"一時ファイルを作成しました: {temp_file}")

        # 3. Pandocのオプション設定 (MathML数式対応) [2]
        args = [
            '-t', 'epub3',
            '--standalone',
            '--mathml',  # iPadのブックアプリで美しく表示させるためのMathML [2]
            f'--metadata=title:{title}',
            '--toc'
        ]

        # 4. 「一時ファイル」を入力として、EPUBへの変換を実行
        print("EPUBへ変換中（MathML適用）...")
        pypandoc.convert_file(
            temp_file,  # 入力を temp_file に変更
            'epub3', 
            format='md', 
            extra_args=args, 
            outputfile=output_file
        )
        print(f"Success: {output_file} が正常に生成されました！")
        
    except OSError:
        print("Error: システムに Pandoc がインストールされていない可能性があります。")
    except RuntimeError as e:
        print(f"Error (Pandoc変換エラー): {e}")
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # 5. 【クリーンアップ】プログラムが成功しても失敗しても、一時ファイルが存在すれば削除する
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"一時ファイルをクリーンアップ（削除）しました: {temp_file}")
            except Exception as delete_error:
                print(f"Warning (一時ファイルの削除失敗): {delete_error}")


if __name__ == "__main__":
    convert_md_to_epub()






if __name__ == "__main__":
    convert_md_to_epub()