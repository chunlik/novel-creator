import argparse
import os
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Build context prompt for an AI writer.")
    parser.add_argument("--chapter", type=str, required=True, help="Chapter number or ID (e.g., '1' or 'Ch1')")
    parser.add_argument("--outline", type=str, help="Path to the outline file for this chapter")
    parser.add_argument("--characters", type=str, nargs='*', default=[], help="List of character names to include (e.g., 周倉 許小小)")
    parser.add_argument("--rules", type=str, nargs='*', default=[], help="List of rule/world files to include (e.g., 直播間 存在校正)")
    parser.add_argument("--output", type=str, default="Prompt_Current.txt", help="Output file name")
    return parser.parse_args()

def read_file_safe(filepath):
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_state_machine():
    state_path = os.path.join("16-作者控制台", "狀態機.md")
    return read_file_safe(state_path)

def search_markdown_files(directory, filenames):
    content_map = {}
    if not os.path.exists(directory):
        return content_map
        
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                name_without_ext = file[:-3]
                if name_without_ext in filenames:
                    filepath = os.path.join(root, file)
                    content_map[name_without_ext] = read_file_safe(filepath)
    
    for name in filenames:
        if name not in content_map:
            print(f"[Warning] Could not find markdown file for: {name} in {directory}")
            
    return content_map

def main():
    args = parse_args()
    output_lines = []
    
    # 1. System Prompt Header
    output_lines.append("# 無限直播間+ - 章節寫作上下文包")
    output_lines.append(f"## 任務：撰寫第 {args.chapter} 章\n")
    output_lines.append("【寫作原則】\n請嚴格遵守以下所有設定與狀態。不可違背 Level-A 規則。維持冷峻、克制的語氣。禁止讓 AI 替主角全知全能。\n")
    output_lines.append("---")
    
    # 2. Hard State (狀態機)
    output_lines.append("\n# [核心狀態] 當前狀態機 (絕對不可違背)")
    state_content = extract_state_machine()
    output_lines.append(state_content if state_content else "狀態機讀取失敗。")
    output_lines.append("---")
    
    # 3. Outline
    if args.outline:
        output_lines.append(f"\n# [本章大綱] {os.path.basename(args.outline)}")
        outline_content = read_file_safe(args.outline)
        output_lines.append(outline_content if outline_content else "大綱讀取失敗。")
        output_lines.append("---")
    
    # 4. Characters
    if args.characters:
        output_lines.append("\n# [角色設定] 本章出場人物")
        char_contents = search_markdown_files("03-角色資料庫", args.characters)
        for char_name, content in char_contents.items():
            output_lines.append(f"\n## 角色：{char_name}")
            output_lines.append(content)
        output_lines.append("---")
        
    # 5. Rules and World Building
    if args.rules:
        output_lines.append("\n# [世界觀與規則] 相關設定")
        # Search both World and Rules directories
        rule_contents_01 = search_markdown_files("01-世界觀", args.rules)
        rule_contents_05 = search_markdown_files("05-系統規則", args.rules)
        rule_contents_04 = search_markdown_files("04-組織勢力", args.rules)
        rule_contents_06 = search_markdown_files("06-副本資料庫", args.rules)
        
        all_rules = {**rule_contents_01, **rule_contents_05, **rule_contents_04, **rule_contents_06}
        for rule_name, content in all_rules.items():
            output_lines.append(f"\n## 設定：{rule_name}")
            output_lines.append(content)
        output_lines.append("---")
        
    # 6. Action instruction
    output_lines.append("\n# [行動指令]")
    output_lines.append(f"請根據上述提供的「大綱」、「狀態機」與「設定檔案」，撰寫第 {args.chapter} 章的正文草稿。")
    
    # Write to output file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))
        
    print(f"[Success] Context successfully built to {args.output}")
    print(f"Included Characters: {', '.join(args.characters)}")
    print(f"Included Rules: {', '.join(args.rules)}")

if __name__ == "__main__":
    main()
