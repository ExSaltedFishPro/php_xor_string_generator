# PHP XOR String Generator

Generate PHP expressions that evaluate to arbitrary strings using only XOR of allowed characters. Useful for simple payload obfuscation or when restricting the character set in PHP source.

## What it does
- Builds a mapping from each byte (0-255) to an XOR tuple drawn from the provided support characters.
- Supports fixed-length tuples to keep all components the same size (default is auto-chosen to cover every byte).
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
- `--fixed-len`: Force a specific tuple length. If omitted, the tool recommends one that can represent all bytes for the given support set.
- `--support-chars`: Characters allowed in each XOR component (default: `0123456789+-*/().~^|&`).

### Notes
- If you pick a fixed length that cannot represent some bytes, encoding those characters raises `UnsupportedCharacterError`.
- Auto-recommended length aims to cover every byte using the supplied support characters.

## Python API
```python
from php_xor_string_generator import XOREncoder

support = XOREncoder.str_to_ord_list("0123456789+-*/().~^|&")
encoder = XOREncoder(support, fixed_len=3)  # omit fixed_len to auto-recommend

php_expr = encoder.to_php_expression("system('id');")
print(php_expr)
```

## FAQ
- **Why fixed length?** PHP strings XOR operations will automatically cut off to the shortest length, so using equal-length tuples keeps XOR parts aligned and predictable; shorter lengths may fail to cover all bytes.
- **How is the recommendation computed?** A BFS finds shortest tuples per byte; the maximum tuple length across all bytes becomes the suggested fixed length.
