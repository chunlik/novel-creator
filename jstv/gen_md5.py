from pathlib import Path
import hashlib

base = Path(__file__).resolve().parent
index_file = base / 'dist' / 'index.js'
md5_file = base / 'dist' / 'index.js.md5'

content = index_file.read_text(encoding='utf-8')
md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
md5_file.write_text(md5 + '\n', encoding='utf-8')
print(md5)
