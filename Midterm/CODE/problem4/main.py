# 定義 AES 使用的不可約多項式 p(x) = x^8 + x^4 + x^3 + x + 1
# 我們用來做有限域 GF(2^8) 上的乘法與反元素運算
MOD_P = 0x12B

def gf_mul(a: int, b: int) -> int:
    """
    在 GF(2^8) 中計算 a * b，模 p(x) 做約簡
    """
    r = 0
    for i in range(8):
        if (b >> i) & 1:
            r ^= a << i
    # 模多項式的約簡：最高可能到 15 次項，需對 MOD_P 左移後消除
    for deg in range(15, 7, -1):
        if (r >> deg) & 1:
            r ^= MOD_P << (deg - 8)
    return r & 0xFF  # 回傳 8-bit 結果

def gf_inv(a: int) -> int:
    """
    在 GF(2^8) 中求 a 的乘法反元素
    """
    if a == 0:
        return 0  # 0 沒有反元素，定義為 0
    for b in range(1, 256):
        if gf_mul(a, b) == 1:
            return b
    raise ValueError(f"No inverse for {a}")

# 定義 affine transform 所用循環矩陣（由 vector 11110000 生成）
_V = [1,0,0,0,1,1,1,1]
M = [[ _V[(j - i) % 8] for j in range(8)] for i in range(8)]

def build_sbox(C: int) -> list[int]:
    """
    建構 S-Box：S(x) = M ⋅ x^{-1} ⊕ C
    C：Affine constant
    """
    sbox = [0]*256
    for x in range(256):
        inv = gf_inv(x)
        y = 0
        for i in range(8):  # 計算 affine transform
            bit = 0
            for j in range(8):
                bit ^= ((inv >> j) & 1) & M[i][j]
            y |= ((bit ^ ((C >> i) & 1)) << i)
        sbox[x] = y
    return sbox

def is_bijective(s: list[int]) -> bool:
    """
    判斷 S-Box 是否為雙射（每個輸入對應唯一輸出）
    """
    return len(set(s)) == 256

def count_fixed_points(s: list[int]) -> int:
    """
    計算 S-Box 中固定點個數：即 S(x) = x 的個數
    """
    return sum(1 for x in range(256) if s[x] == x)

# 嘗試所有 affine 常數 C，找出符合條件（雙射、無固定點）的 C 值
candidates = []
for C in range(256):
    s = build_sbox(C)
    if is_bijective(s) and count_fixed_points(s) == 0:
        candidates.append(C)

if not candidates:
    print("未找到符合條件的 affine constant C")
    exit(1)

# 取出第一個合法 C，建立對應 S-Box
C0 = candidates[0]
SBOX = build_sbox(C0)

# S-Box 安全性評估七項指標

# 1. Bijectivity: 所有輸出值應為唯一
bij_count = len(set(SBOX))

# 2. Non-linearity: 所有非零掩碼對應的非線性度最小值（越高越好）
def walsh_hadamard(f):
    """
    執行 Fast Walsh-Hadamard Transform，用來計算線性近似偏差
    """
    W = f.copy()
    for i in range(8):
        step = 1 << i
        for j in range(256):
            if j & step:
                u, v = W[j ^ step], W[j]
                W[j ^ step], W[j] = u+v, u-v
    return W

min_nl = 256
for u in range(1,256):
    f = [bin(SBOX[x] & u).count("1") & 1 for x in range(256)]
    g = [1 - 2 * v for v in f]  # 將 {0,1} 映射到 {+1, -1}
    W = walsh_hadamard(g)
    maxW = max(abs(w) for w in W)
    nl = 128 - maxW / 2
    min_nl = min(min_nl, nl)

# 3. SAC (Strict Avalanche Criterion)
total_flips = sum(
    bin(SBOX[x] ^ SBOX[x ^ (1<<i)]).count("1")
    for i in range(8) for x in range(256)
)
avg_flips_per_bit = total_flips / (256 * 8)
sac_percent = avg_flips_per_bit / 8 * 100  # SAC 百分比

# 4. Differential Uniformity (DU): 對所有 dx ≠ 0，dy 出現頻率的最大值（愈小愈好）
def differential_uniformity(s):
    maxdu = 0
    for dx in range(1,256):
        cnt = {}
        for x in range(256):
            dy = s[x] ^ s[x^dx]
            cnt[dy] = cnt.get(dy, 0) + 1
        maxdu = max(maxdu, max(cnt.values()))
    return maxdu

du = differential_uniformity(SBOX)

# 5. Linear Approximation Bias (LAB): 最大偏差（愈小愈好）
max_corr = 0
for a in range(1,256):
    h = [1 if bin(a & x).count("1")%2==0 else -1 for x in range(256)]
    for u in range(1,256):
        g = [1 if bin(u & SBOX[x]).count("1")%2==0 else -1 for x in range(256)]
        corr = sum(h[i]*g[i] for i in range(256))
        max_corr = max(max_corr, abs(corr))
bias = max_corr // 2

# 6. Algebraic Degree: 最大布爾輸出函數的代數次數（理想為 7）
def algebraic_degree(truth):
    coef = truth.copy()
    for i in range(8):
        for m in range(256):
            if m & (1<<i):
                coef[m] ^= coef[m ^ (1<<i)]
    return max(bin(m).count("1") for m,v in enumerate(coef) if v)

max_deg = 0
for bit in range(8):
    fb = [(SBOX[x]>>bit)&1 for x in range(256)]
    max_deg = max(max_deg, algebraic_degree(fb))

# 7. Fixed Points
fixed = count_fixed_points(SBOX)

# 結果輸出表格

print(f"# | Criterion                | Target              | Result")
print(f"--|--------------------------|---------------------|-------------------------")
print(f" 1| Bijectivity              | 256 unique values   | {bij_count} unique")
print(f" 2| Non-linearity            | ≥112                | {min_nl:.0f}")
print(f" 3| Strict Avalanche (SAC)   | ~50% bit flips      | {sac_percent:.1f}%")
print(f" 4| Differential Uniformity  | ≤4                  | {du}")
print(f" 5| Linear-approx. bias      | ≤16                 | {bias}")
print(f" 6| Algebraic degree         | 7                   | {max_deg}")
print(f" 7| Fixed-point count        | 0                   | {fixed}")
