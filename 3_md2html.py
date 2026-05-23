import pypandoc

def convert_md_to_html():
    input_file = 'output.md'
    output_file = 'output_local.html'

    # Pandocのオプション設定
    # --standalone: ヘッダーやCSSを含む完全なHTMLを作成
    # -self-contained: 画像などをHTML内に埋め込む (オプション)
    # --katex: 数式の描写。mathjaxはうまくいかず
    # --metadata title="タイトル": ページのタイトルを設定
    # --toc: 目次の作成
    args = [
        '--standalone',
        '--self-contained',
        '--katex',
        '--template=./templates/bootstrap_menu.html',
        '--toc'        
    ]




    try:
        # 変換実行
        output = pypandoc.convert_file(
            input_file, 
            'html', 
            format='md', 
            extra_args=args, 
            outputfile=output_file
        )
        print(f"Success: {output_file} generated.")
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert_md_to_html()