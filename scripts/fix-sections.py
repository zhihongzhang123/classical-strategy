#!/usr/bin/env python3
"""
章节标题修复脚本
将旧版章节标题升级为企业级标准格式
"""

import re
from pathlib import Path

def fix_sections(content):
    """修复章节标题"""
    # 修复"总论" -> "一句话精髓"（如果没有一句话精髓）
    if '## 总论' in content and '## 一句话精髓' not in content:
        # 提取总论内容
        match = re.search(r'## 总论\n\n(.*?)\n(?:---|\n## )', content, re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # 如果第一段包含核心思想，作为一句话精髓
            if '**' in summary or len(summary) < 100:
                content = re.sub(r'## 总论\n\n', '## 一句话精髓\n\n**', content)
                content = re.sub(r'\n(?:---|\n## )', '**\n\n## 核心思想分层解读\n', content, count=1)
    
    # 确保有一句话精髓章节
    if '## 一句话精髓' not in content:
        # 尝试从第一个段落提取
        first_section_match = re.search(r'## (?:总论 | 概述 | 引言)\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if first_section_match:
            first_content = first_section_match.group(1).strip()
            # 创建一句话精髓
            if len(first_content) < 200:
                essence = first_content.split('\n')[0][:80]
                essence_section = f'## 一句话精髓\n\n**{essence}**\n\n'
                content = re.sub(r'## (?:总论 | 概述 | 引言)\n\n', essence_section + '## 核心思想分层解读\n\n', content, count=1)
            else:
                content = re.sub(r'## (?:总论 | 概述 | 引言)\n', '## 核心思想分层解读\n', content, count=1)
                content = '## 一句话精髓\n\n**待补充：用一句话概括本章核心智慧**\n\n' + content
    
    # 修复核心思想标题
    content = re.sub(r'^## 核心思想$', '## 核心思想分层解读', content, flags=re.MULTILINE)
    
    # 修复现代案例标题
    content = re.sub(r'^## 现代案例$', '## 现代案例深度解析', content, flags=re.MULTILINE)
    content = re.sub(r'^## 案例解析$', '## 现代案例深度解析', content, flags=re.MULTILINE)
    content = re.sub(r'^## 案例分析$', '## 现代案例深度解析', content, flags=re.MULTILINE)
    
    # 修复行动指南标题
    content = re.sub(r'^## 行动指南$', '## 可操作的行动指南', content, flags=re.MULTILINE)
    content = re.sub(r'^## 实践指南$', '## 可操作的行动指南', content, flags=re.MULTILINE)
    content = re.sub(r'^## 应用指南$', '## 可操作的行动指南', content, flags=re.MULTILINE)
    
    # 如果没有现代案例章节，添加一个占位符
    if '## 现代案例深度解析' not in content and '## 现代案例' not in content:
        # 在行动指南之前插入
        if '## 可操作的行动指南' in content:
            placeholder = '''## 现代案例深度解析

*待补充：添加 1-2 个现代商业或生活案例*

'''
            content = re.sub(r'\n(## 可操作的行动指南)', f'\n{placeholder}\\1', content)
        elif '## 延伸思考' in content:
            placeholder = '''## 现代案例深度解析

*待补充：添加 1-2 个现代商业或生活案例*

'''
            content = re.sub(r'\n(## 延伸思考)', f'\n{placeholder}\\1', content)
        else:
            # 添加到文件末尾
            content += '\n\n## 现代案例深度解析\n\n*待补充：添加 1-2 个现代商业或生活案例*\n'
    
    # 如果没有行动指南章节，添加一个占位符
    if '## 可操作的行动指南' not in content and '## 行动指南' not in content:
        placeholder = '''## 可操作的行动指南

*待补充：添加 3-5 条具体可操作的建议*

'''
        if '## 延伸思考' in content:
            content = re.sub(r'\n(## 延伸思考)', f'\n{placeholder}\\1', content)
        else:
            content += '\n\n## 可操作的行动指南\n\n*待补充：添加 3-5 条具体可操作的建议*\n'
    
    return content

def process_file(filepath):
    """处理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_sections(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dirs = ['sunzi-bingfa', 'sanshi-liuji', 'daodejing', 'zizhi-tongjian']
    fixed = 0
    
    for base_dir in base_dirs:
        dir_path = Path(base_dir)
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob('*.md'):
            if process_file(str(md_file)):
                print(f'✅ 已修复：{md_file}')
                fixed += 1
    
    print(f'\n{"="*60}')
    print(f'修复完成！共修复 {fixed} 个文件')
    print(f'{"="*60}')

if __name__ == '__main__':
    main()
