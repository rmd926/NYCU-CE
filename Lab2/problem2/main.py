import hashlib
import os

def sha1_hash(data: str) -> str:
    return hashlib.sha1(data.encode('utf-8')).hexdigest()

def crack_sha1(target_hash, password_list_path):
    attempts = 0
    with open(password_list_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            password = line.strip()
            attempts += 1
            if sha1_hash(password) == target_hash:
                return password, attempts
    return None, attempts

def crack_sha1_with_salt(file_path, target_hash, salt):
    attempt_count = 0
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            password = line.strip()
            attempt_count += 1
            salted_password = salt + password
            if sha1_hash(salted_password) == target_hash:
                return password, attempt_count
    return None, attempt_count

def find_plaintext(file_path, hash_to_crack):
    attempts = 0
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for word in file:
            word = word.strip()
            attempts += 1
            if sha1_hash(word) == hash_to_crack:
                return word, attempts
    return None, attempts

def main():
    password_list = os.path.join(os.path.dirname(__file__), '..', 'password.txt')
    targets = [
        {"name": "Easy hash", "hash": "884950a05fe822dddee8030304783e21cdc2b246"},
        {"name": "Medium hash", "hash": "9b467cbabe4b44ce7f34332acc1aa7305d4ac2ba"},
    ]

    for target in targets:
        result, attempts = crack_sha1(target["hash"], password_list)
        if result:
            print(f"Hash: {target['hash']}")
            print(f"Password: {result}")
            print(f"Took {attempts} attempts to crack message.\n")
        else:
            print(f"{target['name']} not found. Attempts: {attempts}\n")

    salt_hash = 'dfc3e4f0b9b5fb047e9be9fb89016f290d2abb06'
    target_hash_leet = '9d6b628c1f81b4795c0266c0f12123c1e09a7ad3'
    real_salt, salt_attempts = find_plaintext(password_list, salt_hash)

    if real_salt:
        print(f"Salt found: {real_salt}")
        print(f"Salt took {salt_attempts} attempts to find.\n")
        matching_word, attempts = crack_sha1_with_salt(password_list, target_hash_leet, real_salt)
        if matching_word:
            print(f"Hash: {target_hash_leet}")
            print(f"Password: {matching_word}")
            print(f"Took {attempts} attempts to crack message.")
        else:
            print(f"Hash: {target_hash_leet}")
            print("Password not found in provided list.")
            print(f"Took {attempts} attempts.")
    else:
        print("Salt not found in provided list. Cannot proceed with Leet hacker hash.")

if __name__ == "__main__":
    main()
