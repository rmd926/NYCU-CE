import hashlib
import os

def generate_keystream(password: str, nonce: bytes, length: int) -> bytes:
    """
    使用 SHAKE128 從密碼和 nonce 派生出指定長度的金鑰流。
    """
    shake = hashlib.shake_128()
    # 將密碼（UTF-8 編碼）與 nonce 拼接，更新到 SHAKE128 中
    shake.update(password.encode('utf-8') + nonce)
    # 輸出指定長度的金鑰流
    return shake.digest(length)

def encrypt(password: str, plaintext: str) -> bytes:
    """
    加密函數：
    1. 生成一個隨機 16 字節的 nonce。
    2. 利用密碼和 nonce 生成與明文等長的金鑰流。
    3. 將明文與金鑰流進行 XOR 運算得到密文。
    4. 將 nonce 拼接在密文前面，方便解密時使用。
    """
    plaintext_bytes = plaintext.encode('utf-8')
    nonce = os.urandom(16)  # 生成 16 字節的隨機 nonce
    keystream = generate_keystream(password, nonce, len(plaintext_bytes))
    # 對明文進行 XOR 加密
    ciphertext_bytes = bytes(a ^ b for a, b in zip(plaintext_bytes, keystream))
    # 將 nonce 與密文連接後返回
    return nonce + ciphertext_bytes

def decrypt(password: str, ciphertext: bytes) -> str:
    """
    解密函數：
    1. 從密文中提取前 16 字節的 nonce。
    2. 利用相同的密碼和 nonce 生成相同長度的金鑰流。
    3. 進行 XOR 運算還原出原始明文。
    """
    nonce = ciphertext[:16]
    ciphertext_bytes = ciphertext[16:]
    keystream = generate_keystream(password, nonce, len(ciphertext_bytes))
    # 利用 XOR 還原明文
    plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext_bytes, keystream))
    return plaintext_bytes.decode('utf-8')

# 示例使用
if __name__ == '__main__':
    password = input("plesase enter your password: ")
    plaintext = input("please enter your plaintext: ")
    print("原文:", plaintext)
    
    ciphertext = encrypt(password, plaintext)
    print("密文 (16 進制):", ciphertext.hex())
    
    decrypted_text = decrypt(password, ciphertext)
    print("解密後:", decrypted_text)
