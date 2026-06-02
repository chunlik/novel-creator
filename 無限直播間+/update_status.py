import os
import re

def update_status_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern for YAML frontmatter
    new_content = re.sub(r'^status:\s*(部分定案|待定)\s*$', 'status: 已定案', content, flags=re.MULTILINE)
    
    # Pattern for tags in YAML
    new_content = re.sub(r'^\s*-\s*部分定案\s*$', '  - 已定案', new_content, flags=re.MULTILINE)
    new_content = re.sub(r'^\s*-\s*待定\s*$', '  - 已定案', new_content, flags=re.MULTILINE)
    
    # Pattern for text inside file
    new_content = new_content.replace('【部分定案】', '【已定案】')
    new_content = new_content.replace('【待定】', '【已定案】')

    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    directories = [
        "01-世界觀",
        "03-角色資料庫",
        "04-組織勢力",
        "05-系統規則",
        "06-副本資料庫",
        "07-篇章大綱",
        "16-作者控制台"
    ]
    
    updated_count = 0
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    if update_status_in_file(filepath):
                        updated_count += 1
                        print(f"Updated: {filepath}")
                        
    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main()
