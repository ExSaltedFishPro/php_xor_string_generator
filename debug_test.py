from php_xor_string_generator import XOREncoder

# 模拟 --blocked-regex "[a-zA-Z0-9]" 后的支持字符
support = list(range(33,48)) + list(range(58,65)) + list(range(91,97)) + list(range(123,127)) + [32]
print("Support chars:", ''.join(chr(c) for c in support))

encoder = XOREncoder(support, intended_input='shell.php')
print('fixed_len:', encoder.fixed_len)
print('dict[46] (.):', encoder.dictionary.get(46))
print('dict[115] (s):', encoder.dictionary.get(115))

# 检查不定长字典
encoder2 = XOREncoder(support)
bfs_dict = encoder2.generate_dictionary()
print('\nBFS dict[46] (.):', bfs_dict.get(46))
print('BFS dict[115] (s):', bfs_dict.get(115))

# 找出需要的最大长度
max_len = 0
for c in 'shell.php':
    o = ord(c)
    if o in bfs_dict:
        if len(bfs_dict[o]) > max_len:
            max_len = len(bfs_dict[o])
            print(f"  char '{c}' (ord={o}) needs {len(bfs_dict[o])} chars: {bfs_dict[o]}")

print(f'\nRecommended max_len for "shell.php": {max_len}')
