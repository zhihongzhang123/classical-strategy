#!/usr/bin/env python3
"""内容质量验证脚本 v4 — 查内容，不查标题；覆盖心法(xinfa/) + 四书逐篇解读

v2 的教训：只验证「章节标题存在性」的空壳闸门，让 21/35 篇「[待补充]」占位符
和跨篇批量复制的同一段案例全绿通过 CI。格式合规 ≠ 内容存在。

v4 按内容类型(profile)套用不同的必需节，其余硬规则两类内容共享：
1. 结构完整：按 profile 的必需节全部存在
2. 禁占位符：任何「待补充」「[行动 1]」式模板空壳
3. 禁跨篇复制：≥40 字段落在两篇以上重复出现（全局，含跨书）——案例必须属于它所在的篇
4. 失效节实质化：心法的「失效条件」/ 四书的「失效边界」≥150 字且 ≥2 条列表项
5. 历史验证含败例：仅心法(xinfa)——只写成功案例的心法是推销
6. 禁词：第三方博主/KOL、交易所名、内部系统名（公开边界）
7. 模板残留：写作纪律注释节必须在成稿中删除

用法：python3 scripts/validate-content.py [目录...]  （默认扫描全部五类内容目录）
退出码：0 = 全部通过；1 = 有违规（CI 失败）
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 内容类型 → (必需节, 失效节标题, 是否要求败例)
PROFILES = {
    "xinfa": (
        ["核心命题", "因果机制", "执行样本", "识别条件",
         "失效条件", "历史验证", "常见误用"],
        "失效条件",
        True,
    ),
    "book": (
        ["一句话精髓", "原文", "分层解读", "市场映射",
         "真实案例", "失效边界", "常见误用", "行动清单"],
        "失效边界",
        False,
    ),
}

# 目录 → profile
DIR_PROFILE = {
    "xinfa": "xinfa",
    "sunzi-bingfa": "book",
    "sanshi-liuji": "book",
    "daodejing": "book",
    "zizhi-tongjian": "book",
}
DEFAULT_DIRS = list(DIR_PROFILE.keys())

# 占位符模式：命中即失败
PLACEHOLDER_PATTERNS = [
    r"待补充", r"\[行动\s*\d+\]", r"\[具体做法\]", r"\[描述案例背景\]",
    r"\[说明如何应用本章智慧\]", r"\[描述结果和启示\]", r"\[总结关键点\]",
    r"\[待补充具体案例名称\]", r"\[检查项", r"\[具体动作\]",
    r"<书名", r"<一句话", r"<古典锚", r"<≤30字", r"<逐字核对", r"<这一篇",
    r"<为什么成立", r"<剥离军事", r"<这条原理", r"<1-2 个真实",
    r"<失灵场景", r"<误用行为>", r"<读者能", r"<chapter", r"TODO", r"TBD", r"XXX",
]

# 禁词：公开边界（第三方博主痕迹 + 交易所身份）
# 注：引擎/记分牌/管线/留痕等「方法论」词不在禁列——公开边界允许方法论复盘，
# 只禁持仓/交易所/金额/第三方 KOL。且「引擎」在四书解读里常是比喻用法（如「反转的引擎」）。
# 「流程自语」（收尾报自己的内部流程）是 X 推文的读者价值规矩，归 x_voice_rules.md，不在本 validator。
# 禁词以 hex 编码存储：源码/仓库搜索不出现第三方名字面量，解码后校验语义不变
BANNED_WORDS = [
    bytes.fromhex("e88081e99bb7").decode(),
    bytes.fromhex("5468654d61726b65744d656d6f").decode(),
    bytes.fromhex("7468656d61726b65746d656d6f").decode(),
    bytes.fromhex("e5b881e5ae89").decode(),
    bytes.fromhex("62696e616e6365").decode(),
    bytes.fromhex("42696e616e6365").decode(),
    bytes.fromhex("4f4b58").decode(),
    bytes.fromhex("6f6b78").decode(),
    bytes.fromhex("4279626974").decode(),
    bytes.fromhex("6279626974").decode(),
    bytes.fromhex("426974676574").decode(),
    bytes.fromhex("626974676574").decode(),
    bytes.fromhex("547261644669").decode(),
    bytes.fromhex("747261646669").decode(),
]

TEMPLATE_MARK = "写作纪律（写完后删除本节"
MIN_INVALIDATION_CHARS = 150
DUP_PARA_MIN_CHARS = 40


def strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\n[\s\S]*?\n---\n", text)
    return text[m.end():] if m else text


def paragraphs(text: str):
    """按空行切段，归一化空白，过滤短段与标题/引用（引用=古典原文，允许跨篇）。"""
    out = []
    for para in re.split(r"\n\s*\n", text):
        p = re.sub(r"\s+", "", para)
        if len(p) >= DUP_PARA_MIN_CHARS and not p.startswith(("#", ">")):
            out.append(p)
    return out


def section_body(text: str, heading: str) -> str:
    m = re.search(r"^##\s+" + re.escape(heading) + r".*?$(.*?)(?=^##\s|\Z)",
                  text, re.M | re.S)
    return m.group(1) if m else ""


def profile_for(path: Path) -> str:
    for part in path.parts:
        if part in DIR_PROFILE:
            return DIR_PROFILE[part]
    return "book"  # 仓库外目录（负样本测试）按四书规格


def validate_file(path: Path, all_paragraphs: dict) -> list:
    errors = []
    raw = path.read_text(encoding="utf-8")
    text = strip_frontmatter(raw)
    required, invalidation_heading, require_fail = PROFILES[profile_for(path)]

    # 1. 结构完整
    for sec in required:
        if not re.search(r"^##\s+" + re.escape(sec), text, re.M):
            errors.append(f"缺少必需节：## {sec}")

    # 2. 占位符
    for pat in PLACEHOLDER_PATTERNS:
        for m in re.finditer(pat, text):
            line_no = text[:m.start()].count("\n") + 1
            errors.append(f"占位符/模板残留：「{m.group(0)}」（约第 {line_no} 行）")

    # 3. 禁词
    for word in BANNED_WORDS:
        if word in text:
            errors.append(f"禁词命中：「{word}」（公开边界）")

    # 4. 模板残留
    if TEMPLATE_MARK in text:
        errors.append("模板的「写作纪律」注释节未删除")

    # 5. 失效节实质化
    body = section_body(text, invalidation_heading)
    body_len = len(re.sub(r"\s+", "", body))
    if body_len < MIN_INVALIDATION_CHARS:
        errors.append(
            f"「{invalidation_heading}」节过短（{body_len} 字 < {MIN_INVALIDATION_CHARS} 字）："
            f"说不出这条原理什么时候失灵 = 鸡汤不是解读")
    if len(re.findall(r"^- ", body, re.M)) < 2:
        errors.append(f"「{invalidation_heading}」至少 2 条（当前 {len(re.findall(r'^- ', body, re.M))} 条）")

    # 6. 心法历史验证含败例
    if require_fail:
        hist = section_body(text, "历史验证")
        if not re.search(r"^- 败", hist, re.M):
            errors.append("历史验证缺「- 败（边界）」条目：只写成功案例的心法是推销")

    # 7. 跨篇重复段落登记（全局）
    for p in paragraphs(text):
        all_paragraphs.setdefault(p, []).append(str(path.relative_to(ROOT)) if _under_root(path) else path.name)

    return errors


def _under_root(path: Path) -> bool:
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False


def main():
    dirs = sys.argv[1:] or DEFAULT_DIRS
    files = []
    for d in dirs:
        base = Path(d) if Path(d).is_absolute() else ROOT / d
        files.extend(sorted(base.glob("*.md")))
    if not files:
        print("❌ 未找到任何内容文件：", dirs)
        return 1

    all_paragraphs: dict = {}
    per_file_failed = 0
    for f in files:
        errors = validate_file(f, all_paragraphs)
        rel = f.relative_to(ROOT) if _under_root(f) else f
        if errors:
            per_file_failed += 1
            print(f"❌ {rel}")
            for e in errors:
                print(f"   - {e}")
        else:
            print(f"✅ {rel}")

    # 跨篇重复检查（全局，含跨书）
    dup_groups = {p: names for p, names in all_paragraphs.items() if len(set(names)) > 1}
    for p, names in sorted(dup_groups.items(), key=lambda kv: kv[1]):
        print(f"❌ 跨篇重复段落（{len(p)} 字）出现在：{', '.join(sorted(set(names)))}")
        print(f"   「{p[:60]}…」")

    total_failed = per_file_failed + len(dup_groups)
    print(f"\n共 {len(files)} 篇文件，{per_file_failed} 篇有单文件问题，{len(dup_groups)} 组跨篇重复")
    if total_failed:
        print(f"验证失败：{total_failed} 处问题。准入标准是说出原理的失效边界 + 每篇内容独立，不是排好版。")
        return 1
    print("验证通过：结构完整、无占位符、无禁词、无跨篇复制、失效节实质化。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
