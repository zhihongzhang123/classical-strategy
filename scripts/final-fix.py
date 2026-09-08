#!/usr/bin/env python3
"""
最终修复脚本 - 彻底修复所有文件结构问题
"""

import re
from pathlib import Path
from datetime import datetime

def fix_file(filepath):
    """彻底修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 步骤 1: 提取并清理 Front Matter
    fm_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return False
    
    fm_content = fm_match.group(1)
    body = content[fm_match.end():]
    
    # 清理 FM 中的 ** 和多余内容
    fm_lines = []
    for line in fm_content.split('\n'):
        line = line.rstrip('*').strip()
        if line and ':' in line:
            key = line.split(':')[0].strip()
            value = ':'.join(line.split(':')[1:]).strip().strip('"\'')
            fm_lines.append(f'{key}: "{value}"' if key in ['last_updated', 'version', 'estimated_reading_time'] else f'{key}: {value}')
    
    # 确保必需的 FM 字段
    required_fm = {
        'version': '"2.0"',
        'last_updated': f'"{datetime.now().strftime("%Y-%m-%d")}"',
        'difficulty': '"入门"',
        'estimated_reading_time': '"8 分钟"'
    }
    
    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            k, v = line.split(':', 1)
            fm_dict[k.strip()] = v.strip()
    
    for k, v in required_fm.items():
        if k not in fm_dict:
            fm_dict[k] = v
    
    # 重建 FM
    new_fm = '---\n' + '\n'.join([f'{k}: {v}' for k, v in fm_dict.items()]) + '\n---\n'
    
    # 步骤 2: 清理和重组正文
    # 移除多余的标题
    body = re.sub(r'^# 道德经.*?核心思想\n+', '', body, flags=re.MULTILINE)
    body = re.sub(r'^# 孙子兵法.*?核心思想\n+', '', body, flags=re.MULTILINE)
    body = re.sub(r'^# 三十六计.*?核心思想\n+', '', body, flags=re.MULTILINE)
    body = re.sub(r'^# 资治通鉴.*?核心思想\n+', '', body, flags=re.MULTILINE)
    
    # 步骤 3: 确保有一句话精髓
    if '## 一句话精髓' not in body:
        # 尝试从现有内容提取
        first_para = re.search(r'^\*\*(.+?)\*\*', body, re.DOTALL)
        if first_para:
            essence = first_para.group(1).strip().split('\n')[0][:80]
            essence_section = f'## 一句话精髓\n\n**{essence}**\n\n'
            body = essence_section + body
        else:
            essence_section = '## 一句话精髓\n\n**待补充：用一句话概括本章核心智慧**\n\n'
            body = essence_section + body
    
    # 步骤 4: 确保有核心思想分层解读
    if '## 核心思想分层解读' not in body:
        if '## 核心思想' in body:
            body = re.sub(r'## 核心思想', '## 核心思想分层解读', body)
        else:
            body = '## 核心思想分层解读\n\n### 第一层：核心概念\n\n[待补充]\n\n### 第二层：深层含义\n\n[待补充]\n\n### 第三层：实践应用\n\n[待补充]\n\n' + body
    
    # 步骤 5: 确保有现代案例深度解析
    if '## 现代案例深度解析' not in body:
        if '## 现代案例' in body:
            body = re.sub(r'## 现代案例', '## 现代案例深度解析', body)
        else:
            # 在行动指南或延伸思考前插入
            if '## 可操作的行动指南' in body:
                body = re.sub(r'\n(## 可操作的行动指南)', '\n## 现代案例深度解析\n\n### 案例一：[待补充]\n\n**背景**：[待补充]\n\n**启示**：[待补充]\n\n\\1', body)
            elif '## 延伸思考' in body:
                body = re.sub(r'\n(## 延伸思考)', '\n## 现代案例深度解析\n\n### 案例一：[待补充]\n\n**背景**：[待补充]\n\n**启示**：[待补充]\n\n\\1', body)
            else:
                body += '\n## 现代案例深度解析\n\n### 案例一：[待补充]\n\n**背景**：[待补充]\n\n**启示**：[待补充]\n'
    
    # 步骤 6: 确保有可操作的行动指南
    if '## 可操作的行动指南' not in body:
        if '## 行动指南' in body:
            body = re.sub(r'## 行动指南', '## 可操作的行动指南', body)
        else:
            if '## 延伸思考' in body:
                body = re.sub(r'\n(## 延伸思考)', '\n## 可操作的行动指南\n\n### 个人层面\n\n1. **[行动 1]**：[具体做法]\n\n### 团队层面\n\n1. **[行动 1]**：[具体做法]\n\n\\1', body)
            else:
                body += '\n## 可操作的行动指南\n\n### 个人层面\n\n1. **[行动 1]**：[具体做法]\n'
    
    # 步骤 7: 确保核心思想有至少 3 个###层级
    core_match = re.search(r'## 核心思想分层解读\n(.*?)(?=\n## [^#])', body, re.DOTALL)
    if core_match:
        core_content = core_match.group(1)
        h3_count = len(re.findall(r'^### ', core_content, re.MULTILINE))
        
        if h3_count < 3:
            # 将## 第 X 章转换为### 
            core_content = re.sub(r'^## (第.+? 章.*?)$', r'### \1', core_content, flags=re.MULTILINE)
            core_content = re.sub(r'^## (第十七章.*?)$', r'### \1', core_content, flags=re.MULTILINE)
            core_content = re.sub(r'^## (第三章.*?)$', r'### \1', core_content, flags=re.MULTILINE)
            
            # 重新计算
            h3_count = len(re.findall(r'^### ', core_content, re.MULTILINE))
            
            # 如果还是不够，添加占位符
            while h3_count < 3:
                core_content += f'\n### 第{h3_count+1}层：深化理解\n\n[待补充]\n'
                h3_count += 1
            
            body = body[:core_match.start()] + '## 核心思想分层解读\n' + core_content + body[core_match.end():]
    
    # 组合最终内容
    new_content = new_fm + '\n' + body
    
    if new_content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    base_dirs = ['sunzi-bingfa', 'sanshi-liuji', 'daodejing', 'zizhi-tongjian']
    fixed = 0
    failed = 0
    
    for base_dir in base_dirs:
        dir_path = Path(base_dir)
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob('*.md'):
            try:
                if fix_file(str(md_file)):
                    print(f'✅ 已修复：{md_file}')
                    fixed += 1
            except Exception as e:
                print(f'❌ 修复失败 {md_file}: {e}')
                failed += 1
    
    print(f'\n{"="*60}')
    print(f'修复完成！成功：{fixed}, 失败：{failed}')
    print(f'{"="*60}')

if __name__ == '__main__':
    main()
