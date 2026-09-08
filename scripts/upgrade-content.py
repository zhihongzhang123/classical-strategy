#!/usr/bin/env python3
"""
批量升级脚本 - 将现有内容升级为企业级标准格式

注意：此脚本生成升级建议，人工审核后执行
"""

import os
import re
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
CONTENT_DIRS = ['sunzi-bingfa', 'shiliu-ce', 'daodejing', 'zizhi-tongjian']

def extract_essence(content: str) -> str:
    """从现有内容中提取或生成一句话精髓"""
    # 尝试找总结性段落
    if "## 总结" in content:
        match = re.search(r'## 总结\n\n(.+?)(?=---|\n##|$)', content, re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # 取第一句作为精髓
            first_sentence = summary.split('。')[0] + '。'
            if len(first_sentence) <= 35:
                return first_sentence
    
    # 尝试找第一段核心内容
    if "## " in content:
        sections = re.split(r'\n## ', content)
        for section in sections[1:]:
            if not section.startswith('总论'):
                first_para = section.split('\n\n')[0].strip()
                if len(first_para) < 50:
                    return first_para[:30] + '...'
    
    return "待补充：用一句话概括本章核心思想。"

def generate_upgrade_report():
    """生成升级报告"""
    report = []
    
    for dir_name in CONTENT_DIRS:
        dir_path = WORKSPACE / dir_name
        if not dir_path.exists():
            continue
        
        for md_file in sorted(dir_path.glob('*.md')):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # 检查 Front Matter
            if not content.startswith('---'):
                issues.append("缺少 YAML Front Matter")
            else:
                fm_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
                if fm_match:
                    fm = fm_match.group(1)
                    required = ['title', 'book', 'chapter', 'chapter_name', 'generated_by', 'generated_date']
                    for field in required:
                        if field not in fm:
                            issues.append(f"缺少 Front Matter 字段：{field}")
                    if 'tags' not in fm:
                        issues.append("建议添加 tags 字段")
                    if 'related_chapters' not in fm:
                        issues.append("建议添加 related_chapters 字段")
            
            # 检查必需章节
            required_sections = [
                ('## 一句话精髓', '一句话精髓'),
                ('## 核心思想', '核心思想'),
                ('### 第.+层', '核心思想分层（至少 3 层）'),
                ('## 现代案例', '现代案例'),
                ('## 行动指南', '行动指南')
            ]
            
            for pattern, name in required_sections:
                if not re.search(pattern, content):
                    issues.append(f"缺少章节：{name}")
            
            # 检查内容长度
            body = re.sub(r'---\n.*?\n---', '', content, flags=re.DOTALL)
            if len(body.strip()) < 500:
                issues.append(f"内容过短（{len(body.strip())}字）")
            
            if issues:
                report.append({
                    'file': str(md_file.relative_to(WORKSPACE)),
                    'issues': issues
                })
    
    return report

if __name__ == '__main__':
    print("=" * 70)
    print("企业级升级报告 - 需要人工审核和手动调整")
    print("=" * 70)
    
    report = generate_upgrade_report()
    
    print(f"\n共发现 {len(report)} 个需要升级的文件:\n")
    
    for item in report[:10]:  # 只显示前 10 个
        print(f"📄 {item['file']}")
        for issue in item['issues'][:5]:
            print(f"   └─ {issue}")
        print()
    
    if len(report) > 10:
        print(f"... 还有 {len(report) - 10} 个文件，详见完整报告")
    
    print("\n" + "=" * 70)
    print("建议操作:")
    print("1. 参考 templates/article-template.md 模板")
    print("2. 参考 daodejing/01-dao-de-ben-zhi.md (已升级示例)")
    print("3. 逐个文件进行人工升级，确保内容质量")
    print("=" * 70)
