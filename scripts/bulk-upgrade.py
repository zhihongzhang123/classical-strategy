#!/usr/bin/env python3
"""
企业级内容批量升级脚本 v2.0
自动将旧格式内容升级为企业级标准格式
"""

import os
import re
from pathlib import Path
from datetime import datetime


def upgrade_front_matter(content, filepath):
    """升级 YAML Front Matter，添加缺失的元数据字段"""
    # 提取现有 front matter
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return content
    
    lines = match.group(1).strip().split('\n')
    fm_dict = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip().strip('"\'')
    
    # 根据书籍类型自动添加标签
    if 'tags' not in fm_dict:
        book = fm_dict.get('book', 'unknown')
        if '孙子兵法' in book:
            fm_dict['tags'] = '["战略规划", "军事思想", "竞争策略"]'
        elif '三十六计' in book:
            fm_dict['tags'] = '["谋略智慧", "处世哲学", "策略思维"]'
        elif '道德经' in book:
            fm_dict['tags'] = '["道家哲学", "人生智慧", "领导力"]'
        elif '资治通鉴' in book:
            fm_dict['tags'] = '["历史智慧", "治国理政", "人性洞察"]'
    
    # 添加关联章节字段
    if 'related_chapters' not in fm_dict:
        fm_dict['related_chapters'] = '[]'
    
    # 添加最后更新时间
    if 'last_updated' not in fm_dict:
        fm_dict['last_updated'] = f'"{datetime.now().strftime("%Y-%m-%d")}"'
    
    # 添加版本号
    if 'version' not in fm_dict:
        fm_dict['version'] = '"2.0"'
    
    # 添加难度等级
    if 'difficulty' not in fm_dict:
        fm_dict['difficulty'] = '"入门"'
    
    # 添加预计阅读时间
    if 'estimated_reading_time' not in fm_dict:
        fm_dict['estimated_reading_time'] = '"8 分钟"'
    
    # 重建 front matter，保持字段顺序一致
    new_fm_lines = []
    for key in ['title', 'book', 'chapter', 'chapter_name', 'tags', 'related_chapters', 
                'generated_by', 'generated_date', 'last_updated', 'version', 'difficulty', 'estimated_reading_time']:
        if key in fm_dict:
            new_fm_lines.append(f'{key}: {fm_dict[key]}')
    
    new_fm = '---\n' + '\n'.join(new_fm_lines) + '\n---\n'
    
    # 替换原有 front matter
    content = re.sub(r'^---\n.*?\n---\n', new_fm, content, flags=re.DOTALL)
    return content

def upgrade_body(content):
    """升级正文内容，统一章节标题并添加扩展内容"""
    # 将"核心思想"改为"核心思想分层解读"
    content = re.sub(r'^## 核心思想$', '## 核心思想分层解读', content, flags=re.MULTILINE)
    
    # 将"现代案例"改为"现代案例深度解析"
    content = re.sub(r'^## 现代案例$', '## 现代案例深度解析', content, flags=re.MULTILINE)
    
    # 将"行动指南"改为"可操作的行动指南"
    content = re.sub(r'^## 行动指南$', '## 可操作的行动指南', content, flags=re.MULTILINE)
    
    # 添加延伸思考章节（如果不存在）
    if '## 延伸思考' not in content and '## 相关章节推荐' not in content:
        # 构建延伸思考内容模板
        extension = '''
## 延伸思考

1. **这个思想的核心本质是什么**？
   - 尝试用一句话概括

2. **如何在我的工作/生活中应用**？
   - 找出一个具体场景

3. **可能的误区是什么**？
   - 避免机械套用

## 相关章节推荐

- 查看同系列其他章节深化理解
- 跨经典对照阅读

---

*本文采用企业级内容标准 v2.0 | 最后更新：''' + datetime.now().strftime("%Y-%m-%d") + '*'
        
        # 找到最后一个##标题的位置
        last_header_match = list(re.finditer(r'^## ', content, re.MULTILINE))
        if last_header_match:
            last_pos = last_header_match[-1].start()
            # 找到该章节的结尾
            next_header = re.search(r'^## ', content[last_pos+3:], re.MULTILINE)
            if next_header:
                insert_pos = last_pos + 3 + next_header.start()
            else:
                insert_pos = len(content)
            content = content[:insert_pos] + '\n' + extension + '\n' + content[insert_pos:]
        else:
            content += '\n' + extension
    
    return content


def process_file(filepath):
    """处理单个文件：检查并执行升级"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 如果已经是 v2.0 版本，跳过处理
    if 'version: "2.0"' in content or "version: '2.0'" in content:
        return False
    
    # 执行升级
    content = upgrade_front_matter(content, filepath)
    content = upgrade_body(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def main():
    """主函数：批量处理所有内容目录"""
    base_dirs = ['sunzi-bingfa', 'sanshi-liuji', 'daodejing', 'zizhi-tongjian']
    upgraded = 0
    skipped = 0
    
    for base_dir in base_dirs:
        dir_path = Path(base_dir)
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob('*.md'):
            if process_file(str(md_file)):
                print(f'✅ 已升级：{md_file}')
                upgraded += 1
            else:
                print(f'⏭️  已跳过 (已是 v2.0): {md_file}')
                skipped += 1
    
    print(f'\n{"="*60}')
    print(f'升级完成！')
    print(f'新升级：{upgraded} 个文件')
    print(f'已跳过：{skipped} 个文件')
    print(f'总计：{upgraded + skipped} 个文件')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
