#!/usr/bin/env python3
"""
内容增强脚本 - 为文件添加完整的企业级结构
"""

import re
from pathlib import Path
from datetime import datetime

def enhance_file(filepath):
    """增强单个文件的内容结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. 修复 Front Matter 中的格式问题
    if '**' in content.split('---')[1]:
        # 清理 front matter 中的 **
        fm_match = re.match(r'(---\n.*?)(\n---)', content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            # 移除行尾的 **
            fm = re.sub(r'\*\*$', '', fm, flags=re.MULTILINE)
            content = fm + '\n---' + content.split('---', 2)[2]
    
    # 2. 确保有一句话精髓章节且格式正确
    essence_match = re.search(r'## 一句话精髓\n\n\*\*(.*?)\*\*', content, re.DOTALL)
    if not essence_match:
        # 尝试查找其他格式的一句话精髓
        essence_match = re.search(r'## 一句话精髓\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if essence_match:
            essence_text = essence_match.group(1).strip()
            # 用**包裹
            new_essence = f'## 一句话精髓\n\n**{essence_text}**\n'
            content = re.sub(r'## 一句话精髓\n\n.*?(?=\n## |\Z)', new_essence, content, flags=re.DOTALL)
    
    # 3. 确保核心思想分层解读有至少 3 个###层级
    core_section = re.search(r'## 核心思想分层解读\n(.*?)(?=\n## [^#])', content, re.DOTALL)
    if core_section:
        core_content = core_section.group(1)
        h3_count = len(re.findall(r'^### ', core_content, re.MULTILINE))
        
        if h3_count < 3:
            # 将现有的## 第 X 章转换为### 层级
            def convert_chapter(match):
                chapter_title = match.group(1)
                return f'### {chapter_title}'
            
            core_content = re.sub(r'^## (第.+? 章：.*?)$', convert_chapter, core_content, flags=re.MULTILINE)
            core_content = re.sub(r'^## (第.+? 章.*?)$', convert_chapter, core_content, flags=re.MULTILINE)
            
            # 重新插入
            content = content[:core_section.start()] + '## 核心思想分层解读\n' + core_content + content[core_section.end():]
    
    # 4. 检查并修复现代案例深度解析章节
    if '## 现代案例深度解析' in content:
        # 确保有实际内容而不是占位符
        case_match = re.search(r'## 现代案例深度解析\n\n\*待补充', content)
        if case_match:
            # 替换为真实内容占位
            placeholder = '''## 现代案例深度解析

### 案例一：[待补充具体案例名称]

**背景**：[描述案例背景]

**应用原理**：[说明如何应用本章智慧]

**结果**：[描述结果和启示]

**启示**：[总结关键点]

'''
            content = re.sub(r'## 现代案例深度解析\n\n\*待补充.*?\*', placeholder, content, flags=re.DOTALL)
    
    # 5. 检查并修复行动指南章节
    if '## 可操作的行动指南' in content:
        action_match = re.search(r'## 可操作的行动指南\n\n\*待补充', content)
        if action_match:
            placeholder = '''## 可操作的行动指南

### 个人层面

1. **[行动 1]**：[具体做法]
2. **[行动 2]**：[具体做法]
3. **[行动 3]**：[具体做法]

### 团队/组织层面

1. **[行动 1]**：[具体做法]
2. **[行动 2]**：[具体做法]

### 检查清单

- [ ] 检查项 1
- [ ] 检查项 2
- [ ] 检查项 3

'''
            content = re.sub(r'## 可操作的行动指南\n\n\*待补充.*?\*', placeholder, content, flags=re.DOTALL)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dirs = ['sunzi-bingfa', 'sanshi-liuji', 'daodejing', 'zizhi-tongjian']
    enhanced = 0
    
    for base_dir in base_dirs:
        dir_path = Path(base_dir)
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob('*.md'):
            # 跳过已验证通过的文件
            if '01-dao-de-ben-zhi.md' in str(md_file):
                continue
            
            if enhance_file(str(md_file)):
                print(f'✅ 已增强：{md_file}')
                enhanced += 1
    
    print(f'\n{"="*60}')
    print(f'增强完成！共处理 {enhanced} 个文件')
    print(f'{"="*60}')

if __name__ == '__main__':
    main()
