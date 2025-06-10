"""
1. 利用Index of Coincidence 估計金鑰長度。
2. 使用卡方檢定根據您提供的頻率分布 (freqMap) 來找出每個子序列的最佳位移，
   復原金鑰。
3. 利用金鑰對密文進行 Vigenère 解密，還原出明文。

"""

# 英文頻率表
freqMap = {
    'A': 0.082, 'B': 0.015, 'C': 0.028, 'D': 0.043, 'E': 0.13,
    'F': 0.022, 'G': 0.02, 'H': 0.061, 'I': 0.07, 'J': 0.0015, 
    'K': 0.0077, 'L': 0.04, 'M': 0.024, 'N': 0.067, 'O': 0.075, 
    'P': 0.019, 'Q': 0.00095, 'R': 0.06, 'S': 0.063, 'T': 0.091, 
    'U': 0.028, 'V': 0.0098, 'W': 0.024, 'X': 0.0015, 'Y': 0.02, 
    'Z': 0.00074
}


def index_of_coincidence(text: str) -> float:
    """
    計算一段文字的同現指數 (IC)，只考慮 A~Z 大寫字母。
    """
    filtered = [c for c in text if c.isalpha()]
    N = len(filtered)
    if N <= 1:
        return 0.0

    freq = {}
    for c in filtered:
        freq[c] = freq.get(c, 0) + 1

    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = N * (N - 1)
    return numerator / denominator

def avg_ic_for_keylen(ciphertext: str, keylen: int) -> float:
    """
    將密文依照 keylen 分割成多個子序列，計算各子序列的 IC，並回傳平均值。
    """
    # 僅保留大寫英文字母
    filtered = [c.upper() for c in ciphertext if c.isalpha()]
    columns = [''] * keylen
    for i, ch in enumerate(filtered):
        columns[i % keylen] += ch

    ics = [index_of_coincidence(col) for col in columns if len(col) > 1]
    if not ics:
        return 0.0
    return sum(ics) / len(ics)

def estimate_key_length(ciphertext: str, max_keylen: int = 12) -> int:
    """
    從 1 到 max_keylen 嘗試估計金鑰長度，
    返回平均 IC 最大的金鑰長度。
    一般來說，IC 越高表示子序列保留較多自然語言特徵，
    常見於單一替換加密。
    """
    best_keylen = 1
    best_ic = 0.0
    for k in range(1, max_keylen + 1):
        ic_val = avg_ic_for_keylen(ciphertext, k)
        if ic_val > best_ic:
            best_ic = ic_val
            best_keylen = k
    return best_keylen


def chi_square_score(text: str) -> float:
    """
    計算 text 與英文頻率分布 (freqMap) 的卡方值，
    text 必須只包含 A~Z 大寫字母，
    值越小代表越接近英文頻率分布。
    """
    total = len(text)
    if total == 0:
        return float('inf')
    
    freq_count = {}
    for c in text:
        freq_count[c] = freq_count.get(c, 0) + 1
    
    chi2 = 0.0
    for letter in freqMap:
        observed = freq_count.get(letter, 0)
        expected = freqMap[letter] * total  # 因為 freqMap 是概率分布
        chi2 += (observed - expected) ** 2 / (expected + 1e-9)
    return chi2

def shift_text(text: str, shift: int) -> str:
    """
    將 text 中的每個字母向前移 shift 位 (Caesar 解密)。
    """
    result = []
    for c in text:
        if 'A' <= c <= 'Z':
            new_char = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            result.append(new_char)
        else:
            result.append(c)
    return "".join(result)

def find_best_shift_for_column(column: str) -> int:
    """
    對單一子序列嘗試 0~25 各種位移，
    返回使卡方值最小的位移量。
    """
    best_shift = 0
    min_chi2 = float('inf')
    for s in range(26):
        shifted = shift_text(column, s)
        chi2 = chi_square_score(shifted)
        if chi2 < min_chi2:
            min_chi2 = chi2
            best_shift = s
    return best_shift

def recover_key(ciphertext: str, keylen: int) -> str:
    """
    將密文依據金鑰長度分割成多個子序列，
    對每個子序列利用卡方檢定找出最佳位移，
    後組合成金鑰 (位移 0 對應 'A', 1 對應 'B', ... )。
    """
    filtered = [c.upper() for c in ciphertext if c.isalpha()]
    columns = [''] * keylen
    for i, ch in enumerate(filtered):
        columns[i % keylen] += ch

    key_chars = []
    for col in columns:
        best_shift = find_best_shift_for_column(col)
        key_char = chr(ord('A') + best_shift)
        key_chars.append(key_char)
    return "".join(key_chars)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """
    使用 Vigenère 密碼對 ciphertext 進行解密，
    key 為金鑰 (僅包含 A~Z)，只處理英文字母，
    其他符號保持不變。
    """
    plaintext = []
    key_index = 0
    key_len = len(key)
    for c in ciphertext:
        if c.isalpha():
            offset_c = ord(c.upper()) - ord('A')
            offset_k = ord(key[key_index % key_len].upper()) - ord('A')
            p = (offset_c - offset_k) % 26
            new_char = chr(p + ord('A'))
            if c.islower():
                new_char = new_char.lower()
            plaintext.append(new_char)
            key_index += 1
        else:
            plaintext.append(c)
    return "".join(plaintext)


def main():
    try:
        with open("problem3ciphertext.txt", "r", encoding="utf-8") as f:
            ciphertext = f.read()
    except FileNotFoundError:
        print("找不到檔案 'problem3ciphertext.txt'，請確認檔案位置或重新上傳。")
        return

    # 估計金鑰長度 (根據提示金鑰長度可能 < 8)
    estimated_keylen = estimate_key_length(ciphertext, max_keylen=8)
    print(f"估計的金鑰長度: {estimated_keylen}")

    # 利用卡方檢定恢復金鑰
    recovered_key = recover_key(ciphertext, estimated_keylen)
    print(f"恢復的金鑰: {recovered_key}")

    # 使用恢復的金鑰進行 Vigenère 解密
    plaintext = vigenere_decrypt(ciphertext, recovered_key)
    print("\n解密後的明文：")
    print(plaintext)

if __name__ == "__main__":
    main()
