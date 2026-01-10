from collections import deque
from typing import Dict, Tuple, List, Optional
import argparse
class XOREncoder:
    class UnsupportedCharacterError(Exception):
        pass

    @staticmethod
    def str_to_ord_list(s: str) -> list[int]:
        return [ord(c) for c in s]

    @staticmethod
    def list_to_str(l: list[int]) -> str:
        return ''.join([chr(i) for i in l])

    def fixed_len_xor_dict(self,support: List[int], n: int) -> Dict[int, Tuple[int, ...]]:
        support = sorted(set(support))
        MAX = 256

        # parent[k][x] = (prev_x, used_char)
        parent: List[List[Optional[tuple[int, int]]]] = [[None] * MAX for _ in range(n + 1)]
        parent[0][0] = (-1, -1)  # 起点标记

        # 分层推进
        for k in range(1, n + 1):
            for prev_x in range(MAX):
                if parent[k - 1][prev_x] is None:
                    continue
                for c in support:
                    x = prev_x ^ c
                    if parent[k][x] is None:  # 只保留一条即可；想要“字典序最小”就靠 support 排序
                        parent[k][x] = (prev_x, c)

        res: Dict[int, Tuple[int, ...]] = {}
        for t in range(MAX):
            if parent[n][t] is None:
                continue  # 这个 t 在长度 n 下不可达
            seq: List[int] = []
            cur_x = t
            for k in range(n, 0, -1):
                prev_x, c = parent[k][cur_x]
                seq.append(c)
                cur_x = prev_x
            seq.reverse()
            res[t] = tuple(seq)

        return res
    def generate_dictionary_fixed_len(self, n: int) -> dict[int, tuple[int, ...]]:
        self.dictionary = self.fixed_len_xor_dict(self.support_chars, n)
        return self.dictionary
    def generate_dictionary(self) -> Dict[int, Tuple[int, ...]]:
        """
        生成: target_byte(0..255) -> 最短tuple(由support_chars组成)，使得 XOR(tuple)=target_byte
        使用 BFS 在 8-bit XOR 状态空间上求无权最短路。
        """
        MAX = 256
        dist = [-1] * MAX
        parent = [-1] * MAX      # parent[state] = previous_state
        used = [-1] * MAX        # used[state] = which char XOR'd to reach this state
        q = deque()
        dist[0] = 0
        q.append(0)
        # 为了在多解时更稳定（例如想要字典序更小的 tuple），可以排序
        support = sorted(self.support_chars)

        while q:
            x = q.popleft()
            for c in support:
                y = x ^ c
                if dist[y] == -1:
                    dist[y] = dist[x] + 1
                    parent[y] = x
                    used[y] = c
                    q.append(y)

        d: Dict[int, Tuple[int, ...]] = {}
        for v in range(MAX):
            if dist[v] == -1:
                continue  # 该byte不可由support_chars生成
            path: List[int] = []
            cur = v
            while cur != 0:
                path.append(used[cur])
                cur = parent[cur]
            d[v] = tuple(reversed(path))

        self.dictionary = d
        return d

    def __init__(self, support_chars: list[int],fixed_len=None):
        if fixed_len:
            assert fixed_len >1
            self.fixed_len = fixed_len
        for x in support_chars:
            if not isinstance(x, int) or not (0 <= x <= 255):
                raise ValueError(f"support_chars contains invalid byte: {x!r}")
        seen = set()
        self.support_chars = [x for x in support_chars if not (x in seen or seen.add(x))]

        self.dictionary: dict[int, Tuple[int, ...]] = {}
        if fixed_len is None:
            self.fixed_len = self.recommend_fixed_len()
            self.generate_dictionary_fixed_len(self.fixed_len)
        else:
            self.generate_dictionary_fixed_len(fixed_len)

    def print_dictionary(self):
        for k in range(256):
            if self.dictionary.get(k) is None:
                continue
            v = self.dictionary[k]
            if isinstance(v, str):
                print(f"{k:3}: '{v}'")
            else:
                print(f"{k:3}: {v}")

    def to_php_expression(self, s: str) -> str:
        parts: List[str] = []
        s = self.str_to_ord_list(s)
        targets = []
        for i in s:
            if self.dictionary.get(i) is None or len(self.dictionary.get(i)) != self.fixed_len:
                raise XOREncoder.UnsupportedCharacterError(f"Character {chr(i)!r} (ord={i}) not supported.")
            targets.append(self.dictionary.get(i))
        for i in range(self.fixed_len):
            part = ""
            if s[i] not in self.dictionary:
                raise XOREncoder.UnsupportedCharacterError(f"Character {s[i]!r} (ord={ord(s[i])}) not supported.")
            for t in targets:
                part += chr(t[i])
            parts.append(part)
        return '^'.join("'"+parts+"'" for parts in parts)
    
    def recommend_fixed_len(self) -> int:
        dic = self.generate_dictionary()
        max_len = 0
        for k, v in dic.items():
            if len(v) > max_len:
                max_len = len(v)
        return max_len

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PHP XOR string literals.")
    parser.add_argument("string", help="The string to encode.")
    parser.add_argument("--fixed-len", type=int, default=3, help="Fixed length of XOR components.")
    parser.add_argument("--support-chars", type=str, default="0123456789+-*/().~^|&", help="Characters to use for XOR encoding.")
    args = parser.parse_args()
    encoder = XOREncoder(XOREncoder.str_to_ord_list(args.support_chars), fixed_len=args.fixed_len)

    try:
        php_literal = encoder.to_php_expression(args.string)
        print(php_literal)
    except XOREncoder.UnsupportedCharacterError as e:
        print(f"Error: {e}")