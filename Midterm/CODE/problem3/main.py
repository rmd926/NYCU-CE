"""
Problem 3: Berlekamp–Massey vs EEA on a Very Short Sequence

此程式同時實作：
  (1) Berlekamp–Massey 演算法，求解 minimal polynomial C_BM(x)；
  (2) Extended Euclidean Algorithm，求解 minimal polynomial C_EEA(x)。

輸入序列：
    s = (0,0,1,1,0,1,0,1,1)
"""

from sympy import symbols, Poly, GF

def berlekamp_massey(s):
    """
    輸入：
      s -- 二進位序列 list[int]
    回傳：
      monic 的 Sympy Poly 物件，為 minimal polynomial over GF(2)
    """
    n = len(s)
    C = [1] + [0]*n
    B = [1] + [0]*n
    L = 0
    m = -1
    for N in range(n):
        # 計算 discrepancy d
        d = s[N]
        for i in range(1, L+1):
            d ^= (C[i] & s[N-i])
        if d == 1:
            T = C.copy()
            # C(x) ← C(x) − x^(N−m)·B(x)
            for j in range(0, n - N + m):
                C[N-m+j] ^= B[j]
            if 2*L <= N:
                L, B, m = N+1-L, T, N
    # 組成 monic Poly
    x = symbols('x')
    poly = Poly(sum(c*x**i for i,c in enumerate(C[:L+1])), x, domain=GF(2))
    return poly.set_modulus(2).monic()

def eea_minpoly(s):
    """
    輸入：
      s -- 二進位序列 list[int]
    回傳：
      monic 的 Sympy Poly 物件，為 minimal polynomial over GF(2)
    實作說明：
      1. 以 berlekamp_massey 求得線性複雜度 L；
      2. 設 A(x)=x^(2L)，S(x)=sum s_i x^i；
      3. 手動執行 EEA，當下一階 remainder deg < L 時中斷；
      4. 當前 v 對應 minimal polynomial，最後做 monic 正規化。
    """
    x = symbols('x')
    # (1) 求 L
    Cbm = berlekamp_massey(s)
    L   = Cbm.degree()
    # (2) 建構多項式
    S = Poly(sum(bit * x**i for i,bit in enumerate(s)), x, domain=GF(2)).set_modulus(2)
    A = Poly(x**(2*L), x, domain=GF(2)).set_modulus(2)
    # (3) 初始 EEA 變數
    r0, r1 = A, S
    u0, u1 = Poly(1, x, domain=GF(2)), Poly(0, x, domain=GF(2))
    v0, v1 = Poly(0, x, domain=GF(2)), Poly(1, x, domain=GF(2))
    # 執行至 deg(r1) < L 時停止
    while r1.degree() >= L:
        q  = r0.quo(r1)      # 商
        r2 = r0.rem(r1)      # 餘式
        u2 = u0 - q * u1
        v2 = v0 - q * v1
        # 更新
        r0, r1 = r1, r2
        u0, u1 = u1, u2
        v0, v1 = v1, v2
    # (4) 取 v1 並正規化為 monic
    return v1.set_modulus(2).monic()

if __name__ == '__main__':
    seq = [0,0,1,1,0,1,0,1,1]
    Cbm = berlekamp_massey(seq)
    Cee = eea_minpoly(seq)
    print("【BM minimal polynomial】", Cbm.as_expr())
    print("【EEA minimal polynomial】", Cee.as_expr())
