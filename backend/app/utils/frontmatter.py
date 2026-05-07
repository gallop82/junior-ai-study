import yaml


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    使用标准的 PyYAML 解析 Markdown 头部元数据。
    支持多行文本 (|)、嵌套结构等高级 YAML 语法。
    """
    if not text.startswith("---"):
        return {}, text

    # 按 --- 分割，取中间部分作为 YAML，后半部分作为正文
    # split("---", 2) 会得到 ['', 'YAML内容', '正文内容']
    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    yaml_block = parts[1].strip()
    body = parts[2].lstrip()  # 保留正文前的换行，但去掉多余空格

    try:
        # 使用安全加载模式
        metadata = yaml.safe_load(yaml_block)
        if not isinstance(metadata, dict):
            metadata = {}
    except Exception:
        # 如果解析失败（格式严重错误），回退为空字典
        metadata = {}

    return metadata, body

