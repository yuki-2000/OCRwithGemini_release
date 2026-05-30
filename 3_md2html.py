import pypandoc
import os
import base64
import mimetypes
import re


def embed_images_as_base64(html_file, resource_path):
    with open(html_file, encoding='utf-8') as f:
        html = f.read()

    def repl(m):
        src = m.group(1)
        img_path = os.path.join(str(resource_path), src)
        if not os.path.exists(img_path):
            print(f"  Warning: image not found: {src}  (in {html_file})")
            return m.group(0)
        mime = mimetypes.guess_type(img_path)[0] or 'image/png'
        b64 = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
        return f'src="data:{mime};base64,{b64}"'

    html = re.sub(r'src="([^"]+\.(?:png|jpg|jpeg|gif))"', repl, html)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)



def convert_md_to_html():
    input_file = 'output.md'
    output_file = 'output_local.html'

    title = os.path.splitext(os.path.basename(input_file))[0]

    # Pandocのオプション設定
    # --standalone: ヘッダーやCSSを含む完全なHTMLを作成
    # -self-contained: 画像などをHTML内に埋め込む (オプション)
    # --katex: 数式の描写。mathjaxはうまくいかず
    # --metadata title="タイトル": ページのタイトルを設定
    # --toc: 目次の作成
    
    #args = [
    #    '--standalone',
    #    '--self-contained',
    #    '--katex',
    #    '--template=./templates/bootstrap_menu2.html',
    #    '--toc'        
    #]
    
    args = [
        '--standalone',
        #'--self-contained', #数式SVG埋め込みと相性が
        #'--katex', #数式はhtml側で
        '--mathjax',
        '--template=./templates/bootstrap_menu2.html',
        '--toc',        
        f'--resource-path={resource_path}',
        f'--metadata=title:{title}',
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