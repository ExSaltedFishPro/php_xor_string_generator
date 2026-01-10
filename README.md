# PHP XOR String Generator

Generate a PHP Expression that equals to the given string using XOR operations. This can be useful for obfuscating strings in PHP code.

## Usage

```shell
python php_xor_string_generator.py "system('id');" --fixed-len 3 --support-chars "0123456789+-*/().~^|&"
```
This will output a PHP expression that evaluates to `system('id');` when executed.
```python
from php_xor_string_generator import XOREncoder
encoder = XOREncoder(XOREncoder.str_to_ord_list("system('id');"))
php_expression = encoder.to_php_expression("system('id');")
print(php_expression)
```

## Arguments

`0123456789+-*/().~^|&`

It needs fixed length of 3 to cover all bytes.

You can customize the supported characters and fixed length as needed.

The script will automatically recommend a fixed length based on the supported characters if not provided.

You can also use the `recommend_fixed_len` method to get a recommended fixed length based on the supported characters.

The recommended fixed length is calculated to ensure all byte values (0-255) can be represented using the provided supported characters. But if you want to use a lower fixed length, you can specify it manually,but it may not cover all byte values and could raise an error if the string contains unsupported characters.
