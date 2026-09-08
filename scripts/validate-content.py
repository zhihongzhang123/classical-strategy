#!/usr/bin/env python3
"""
内容质量验证脚本 - 企业级标准

验证所有 Markdown 文件是否符合企业级质量标准：
- YAML Front Matter 完整性
- 必需章节存在性
- 内容长度合理性
- 格式规范性
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 配置项
WORKSPACE = Path(__file__).parent.parent  # 工作区根目录
CONTENT_DIRS = ['sunzi-bingfa', 'sanshi-liuji', 'daodejing', 'zizhi-tongjian']  # 内容目录列表
REQUIRED_FRONT_MATTER = ['title', 'book', 'chapter', 'chapter_name', 'generated_by', 'generated_date']  # 必需的 Front Matter 字段
REQUIRED_SECTIONS = ['一句话精髓', '核心思想分层解读', '现代案例深度解析', '可操作的行动指南']  # 必需的章节标题


def validate_front_matter(content: str, filepath: Path) -> Tuple[bool, List[str]]:
    """验证 YAML Front Matter 的完整性和格式"""
    errors = []
    
    # 检查是否有 Front Matter
    if not content.startswith('---'):
        errors.append("缺少 YAML Front Matter (应以 --- 开头)")
        return False, errors
    
    # 提取 Front Matter
    match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("YAML Front Matter 格式错误")
        return False, errors
    
    front_matter = match.group(1)
    
    # 检查必需字段是否存在
    for field in REQUIRED_FRONT_MATTER:
        if field not in front_matter:
            errors.append(f"缺少必需字段：{field}")
    
    return len(errors) == 0, errors


def validate_sections(content: str, filepath: Path) -> Tuple[bool, List[str]]:
    """验证必需章节是否存在且结构完整"""
    errors = []
    
    # 检查每个必需章节
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in content:
            errors.append(f"缺少必需章节：{section}")
    
    # 检查核心思想是否有分层（支持多种格式）
    if "## 核心思想分层解读" in content or "## 核心思想" in content:
        # 查找所有###层级的标题
        h3_matches = re.findall(r'^### (.+?)$', content, re.MULTILINE)
        subsection_count = len(h3_matches)
        
        # 也检查"第 X 层"格式
        layer_count = len(re.findall(r'### 第.+层', content))
        
        # 取较大值作为有效分层数
        effective_count = max(subsection_count, layer_count)
        
        if effective_count < 3:
            errors.append(f"核心思想分层不足（至少 3 层，当前{effective_count}层）")
    
    return len(errors) == 0, errors


def validate_content_length(content: str, filepath: Path) -> Tuple[bool, List[str]]:
    """验证正文字数是否在合理范围内"""
    errors = []
    
    # 移除 Front Matter
    content_body = re.sub(r'---\n.*?\n---', '', content, flags=re.DOTALL)
    word_count = len(content_body.strip())
    
    if word_count < 500:
        errors.append(f"内容过短（{word_count}字，建议至少 500 字）")
    elif word_count > 5000:
        errors.append(f"内容过长（{word_count}字，建议不超过 5000 字）")
    
    return len(errors) == 0, errors


def validate_essence_length(content: str, filepath: Path) -> Tuple[bool, List[str]]:
    """验证一句话精髓的长度是否符合要求"""
    errors = []
    
    match = re.search(r'## 一句话精髓\n\n\*\*(.+?)\*\*', content)
    if match:
        essence = match.group(1).strip()
        if len(essence) > 30:
            errors.append(f"一句话精髓过长（{len(essence)}字，建议不超过 30 字）")
    else:
        errors.append("未找到一句话精髓内容")
    
    return len(errors) == 0, errors


def validate_file(filepath: Path) -> Dict:
    """验证单个文件的完整性和质量"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 定义验证器列表：(验证名称，验证函数)
        validators = [
            ('Front Matter', validate_front_matter),
            ('章节结构', validate_sections),
            ('内容长度', validate_content_length),
            ('精髓长度', validate_essence_length),
        ]
        
        results = {}
        all_passed = True
        
        # 依次执行所有验证器
        for name, validator in validators:
            passed, errors = validator(content, filepath)
            results[name] = {'passed': passed, 'errors': errors}
            if not passed:
                all_passed = False
        
        return {
            'filepath': str(filepath.relative_to(WORKSPACE)),
            'passed': all_passed,
            'results': results
        }
    
    except Exception as e:
        return {
            'filepath': str(filepath.relative_to(WORKSPACE)),
            'passed': False,
            'results': {'error': {'passed': False, 'errors': [str(e)]}}
        }


def main():
    """主函数：执行批量验证并输出报告"""
    print("=" * 60)
    print("企业级内容质量验证")
    print("=" * 60)
    
    # 收集所有内容文件
    all_files = []
    for dir_name in CONTENT_DIRS:
        dir_path = WORKSPACE / dir_name
        if dir_path.exists():
            all_files.extend(dir_path.glob('*.md'))
    
    if not all_files:
        print("\n❌ 未找到任何 Markdown 文件")
        sys.exit(1)
    
    print(f"\n📁 检测到 {len(all_files)} 个内容文件\n")
    
    results = []
    passed_count = 0
    
    # 逐个验证文件
    for filepath in sorted(all_files):
        result = validate_file(filepath)
        results.append(result)
        if result['passed']:
            passed_count += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} {result['filepath']}")
        
        # 显示失败文件的详细错误信息
        if not result['passed']:
            for check_name, check_result in result['results'].items():
                if isinstance(check_result, dict) and not check_result.get('passed', True):
                    for error in check_result.get('errors', []):
                        print(f"   └─ {check_name}: {error}")
    
    print("\n" + "=" * 60)
    print(f"验证结果：{passed_count}/{len(results)} 通过")
    print("=" * 60)
    
    if passed_count == len(results):
        print("\n🎉 所有内容符合企业级质量标准！")
        sys.exit(0)
    else:
        print(f"\n⚠️  {len(results) - passed_count} 个文件需要修复")
        sys.exit(1)


if __name__ == '__main__':
    main()
