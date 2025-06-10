"""
Q3: 以學生證號作為種子，進行區塊鏈挖礦，每個區塊成功時僅記錄一行。
符合題目格式：
    1) [preImage]
    2) [Round X without nonce] ... 或 [Round X with nonce deadbeef] ...
    3) [EROR] ...
"""

import hashlib
import time

def sha256_hash(data: str) -> str:
    """回傳 data 的 SHA-256 雜湊值（16進位小寫）。"""
    return hashlib.sha256(data.encode()).hexdigest()

def get_current_time() -> str:
    """回傳當前時間字串，格式：YYYY/MM/DD HH:MM:SS。"""
    return time.strftime("%Y/%m/%d %H:%M:%S")

def mine_block(previous_hash: str, target_prefix: str):
    """
    從 nonce=0 逐一嘗試到 0xffffffff，
    若計算出的區塊哈希 (previous_hash + nonce_hex) 符合 target_prefix 則回傳 (block_hash, nonce_hex)；
    否則回傳 (None, None)。
    """
    nonce = 0
    max_nonce = 0xffffffff
    while nonce <= max_nonce:
        nonce_hex = format(nonce, '08x')
        candidate = previous_hash + nonce_hex
        candidate_hash = sha256_hash(candidate)
        if candidate_hash.startswith(target_prefix):
            return candidate_hash, nonce_hex
        nonce += 1
    return None, None

if __name__ == "__main__":
    # 1. 以學生證號作為種子 (範例：313553024)
    student_id = "313553024"
    preImage = sha256_hash(student_id)

    # 2. 建立日誌暫存，並記錄 preImage
    log_entries = []
    log_entries.append(f"{get_current_time()} [INFO] [preImage] {preImage}")

    # 3. 決定起始區塊：比較 preImage 與 student_id，第一個不相符的位置即為 starting_block
    starting_block = 1
    for i in range(min(len(student_id), len(preImage))):
        if preImage[i] != student_id[i]:
            starting_block = i + 1
            break

    # 4. 挖礦流程
    previous_hash = preImage
    total_rounds = 6  # 至少挖到學生證前7位
    for round_num in range(starting_block, starting_block + total_rounds):
        target_prefix = student_id[:round_num]

        # 先檢查是否已經符合 (without nonce)
        if previous_hash.startswith(target_prefix):
            # 若符合，僅記錄一行成功訊息
            log_entries.append(f"{get_current_time()} [INFO] [Round {round_num} without nonce] {previous_hash}")
            continue

        # 若不符合，則進行 with nonce 的挖礦嘗試
        block_hash, nonce_hex = mine_block(previous_hash, target_prefix)
        if block_hash:
            # 成功挖到符合條件的區塊 => 僅記錄一行
            log_entries.append(f"{get_current_time()} [INFO] [Round {round_num} with nonce {nonce_hex}] {block_hash}")
            previous_hash = block_hash
        else:
            # 未找到符合要求的區塊 => 僅記錄一行錯誤訊息
            log_entries.append(f"{get_current_time()} [EROR] [Round {round_num}] not found with running out of nonce")
            break

    # 5. 將日誌寫入 logger.log 檔案
    with open("logger_.log", "w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(entry + "\n")
