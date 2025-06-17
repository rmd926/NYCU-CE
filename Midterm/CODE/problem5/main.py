import random

# ========= 常數時間查表 (Constant-Time LUT) 實作 =========
def ct_lookup(table: list[int], idx: int) -> int:
    """
    常數時間查表：避免快取側信道
    table: 長度 256 的 int list
    idx: 查表索引 (0 <= idx < 256)
    """
    result = 0
    for i, val in enumerate(table):
        mask = -int(i == idx)  # True -> -1 (全 1), False -> 0
        result ^= val & mask
    return result

def build_mul_tables():
    """
    產生 GF(2^8) 乘法查表 mul2 (x*2) 與 mul3 (x*3)
    """
    mul2 = [0] * 256
    mul3 = [0] * 256
    for x in range(256):
        y = ((x << 1) ^ 0x1b) & 0xff if (x & 0x80) else (x << 1) & 0xff
        mul2[x] = y
        mul3[x] = y ^ x
    return mul2, mul3

def mixcol_ct(col_bytes: list[int], mul2: list[int], mul3: list[int]) -> list[int]:
    """
    使用常數時間 LUT 計算單一 MixColumns 欄（4 bytes）
    回傳 4 bytes 列表
    """
    a0, a1, a2, a3 = col_bytes
    y0 = ct_lookup(mul2, a0) ^ ct_lookup(mul3, a1) ^ a2 ^ a3
    y1 = a0 ^ ct_lookup(mul2, a1) ^ ct_lookup(mul3, a2) ^ a3
    y2 = a0 ^ a1 ^ ct_lookup(mul2, a2) ^ ct_lookup(mul3, a3)
    y3 = ct_lookup(mul3, a0) ^ a1 ^ a2 ^ ct_lookup(mul2, a3)
    return [y0, y1, y2, y3]

# ========= 位切 (Bit-Sliced) 實作 =========
def xtime32(x: int) -> int:
    """
    向量化 GF(2^8) xtime，對 4 bytes 同時運算。
    """
    m = (x & 0x7f7f7f7f) << 1
    h = (x & 0x80808080) >> 7
    return (m ^ (h * 0x1b)) & 0xffffffff

def ror8(x: int) -> int:
    """
    對 32-bit word 右旋 8 bits (1 byte)
    """
    return ((x >> 8) | ((x & 0xff) << 24)) & 0xffffffff

def mixcol_bitslice(col: int) -> int:
    """
    位切 MixColumns：單一 4-byte 欄位以 32-bit vector 計算。
    回傳 32-bit 結果 (packed 4 bytes)
    """
    a = col
    b = ror8(a)
    c = ror8(b)
    d = ror8(c)
    return xtime32(a) ^ (xtime32(b) ^ b) ^ c ^ d

# ========= 驗證 =========
if __name__ == "__main__":
    # 建立乘法表
    mul2, mul3 = build_mul_tables()

    # 測試 MixColumns 欄一致性
    for _ in range(10):
        col = [random.randrange(256) for _ in range(4)]
        # CT-LUT 方法
        ct_res = mixcol_ct(col, mul2, mul3)
        ct_word = ct_res[0] | (ct_res[1] << 8) | (ct_res[2] << 16) | (ct_res[3] << 24)
        # Bit-sliced 方法
        col_word = col[0] | (col[1] << 8) | (col[2] << 16) | (col[3] << 24)
        bs_word = mixcol_bitslice(col_word)
        assert bs_word == ct_word, f"Mismatch: CT-LUT=0x{ct_word:08x}, bitslice=0x{bs_word:08x}"
        print(f"Column {col} -> 0x{ct_word:08x} (OK)")
    print("所有測試通過：CT-LUT 與 Bit-Sliced MixColumns 結果一致。")
