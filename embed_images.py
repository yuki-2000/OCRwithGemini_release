# -*- coding: utf-8 -*-

import sys, os, base64, mimetypes, re

html_file, resource_path = sys.argv[1], sys.argv[2]
with open(html_file, encoding='utf-8') as f:
    html = f.read()

def repl(m):
    src = m.group(1)
    img_path = os.path.join(resource_path, src)
    if not os.path.exists(img_path):
        print(f"  Warning: image not found: {src}  (in {html_file})")
        return m.group(0)
    mime = mimetypes.guess_type(img_path)[0] or 'image/png'
    b64 = base64.b64encode(open(img_path, 'rb').read()).decode('ascii')
    return f'src="data:{mime};base64,{b64}"'

html = re.sub(r'src="([^"]+\.(?:png|jpg|jpeg|gif))"', repl, html)
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Embedded images into {html_file}")