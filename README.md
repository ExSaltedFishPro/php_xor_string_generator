# PHP XOR String Generator

Generate PHP expressions that evaluate to arbitrary strings using only XOR of allowed characters. Useful for simple payload obfuscation or when restricting the character set in PHP source.

## What it does
- Builds a mapping from each byte (0-255) to an XOR tuple drawn from the provided support characters.
- Supports fixed-length tuples to keep all components the same size (default is auto-chosen to cover all reachable bytes).
- Exposes both a CLI and a Python API.

## Requirements
- Python 3.9+ (uses type-hinted builtins like `list[int]`).

## CLI usage
```shell
python php_xor_string_generator.py "system('id');" --fixed-len 3 --support-chars "0123456789+-*/().~^|&"
```
Outputs a PHP expression such as `'0+'^'4*'^'…'` that evaluates to the original string.

### Arguments
- `string` (positional): The string to encode.
- `--fixed-len`: Force a specific tuple length. If omitted, the tool recommends one that can represent all reachable bytes for the given support set.
- `--support-chars`: Characters allowed in each XOR component. If omitted, defaults to `0-9`, `a-z`, `A-Z`, punctuation, and space (safe mode).
- `--support-regex`: Regex pattern used to add support characters from printable ASCII (merged with `--support-chars`).
- `--blocked-chars`: Characters to exclude from the final support set.
- `--blocked-regex`: Regex pattern to exclude characters from the final support set.
- `--unsafe`: Include all printable characters (including `'` and `\`) in the support set and enable escaping when emitting PHP string parts.

### Notes
- If you pick a fixed length that cannot represent some bytes, encoding those characters raises `UnsupportedCharacterError`.
- Auto-recommended length aims to cover every reachable byte using the supplied support characters.
- If some bytes are unreachable with your support set, encoding those characters will fail even with auto length.
- In safe mode, `'` and `\` are removed from the support set to avoid breaking PHP string literals.

## Python API
```python
from php_xor_string_generator import XOREncoder

support = XOREncoder.str_to_ord_list("0123456789+-*/().~^|&")
encoder = XOREncoder(support, fixed_len=3)  # omit fixed_len to auto-recommend

php_expr = encoder.to_php_expression("system('id');")
print(php_expr)
```

## 原理与工作流程
1. **支持字符集合**：将允许使用的字符集转换为字节列表（0~255），作为 XOR 组件的候选集合。
2. **字节到 XOR 组件的映射**：
   - 固定长度模式：使用分层动态规划（层数为 `fixed_len`）遍历 XOR 状态空间，构建 `target_byte -> tuple` 的映射。
   - 自动推荐模式：先用 BFS 在 XOR 状态空间中找到每个字节的最短 XOR 组合，再以最长组合长度作为推荐的 `fixed_len`。
3. **字符串编码**：把目标字符串按字节拆分，逐字节查表得到固定长度的 XOR 组件元组，然后按位置拼接成多个同长度字符串，最终以 `'^'` 连接成 PHP 表达式。
4. **安全模式处理**：默认剔除 `'` 与 `\`，避免破坏 PHP 字符串字面量；若启用 `--unsafe`，则允许全部可打印字符并进行必要的转义。

## 功能解析
- **支持固定长度 XOR**：确保每个 XOR 片段长度一致，避免 PHP XOR 规则导致的短字符串截断问题。
- **自动推荐长度**：在给定字符集合下，自动给出可以覆盖全部可达字节的最短统一长度。
- **字符集过滤**：支持白名单（`--support-chars`/`--support-regex`）与黑名单（`--blocked-chars`/`--blocked-regex`）组合，用于适配受限字符场景。
- **安全与不安全模式**：
  - 安全模式默认移除引号和反斜杠，保证生成的 PHP 字符串更稳定。
  - 不安全模式允许更大字符集，并对字符串组件进行转义处理。

## 未直接使用的方法说明（未在 CLI 主流程中显式调用）
- `list_to_str`：将字节列表转回字符串，主要用于调试或在外部脚本中快速查看字节序列的可读形式。
- `print_dictionary`：打印当前字典的映射关系，便于检查可达字节与对应 XOR 组件。
- `generate_dictionary`：使用 BFS 生成“最短 XOR 组合”字典，仅用于推荐长度或外部场景分析；CLI 默认走固定长度生成逻辑。
- `recommend_fixed_len_with_target`：根据指定目标字符串计算最小可用长度，通常用于嵌入到外部工具中按输入动态决定长度。

## FAQ
- **Why fixed length?** PHP strings XOR operations will automatically cut off to the shortest length, so using equal-length tuples keeps XOR parts aligned and predictable; shorter lengths may fail to cover all bytes.
- **How is the recommendation computed?** A BFS finds shortest tuples per byte; the maximum tuple length across all bytes becomes the suggested fixed length.
