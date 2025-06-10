def compute_ic(text: str) -> float:
    """
    Compute and return the Index of Coincidence (IC) for the given text.
    text: input ciphertext or plaintext (string).
    Returns: IC value (float)
    """
    # Filter the text: keep only alphabetic characters (A-Z, a-z), ignore spaces and punctuation
    filtered = [c.upper() for c in text if c.isalpha()]
    N = len(filtered)  # Total number of letters

    # If there are too few letters, return 0 to avoid division by zero
    if N <= 1:
        return 0.0

    # Count the occurrences of each letter
    freq = {}
    for char in filtered:
        freq[char] = freq.get(char, 0) + 1

    # Calculate the numerator: sum( f_i * (f_i - 1) )
    numerator = sum(f * (f - 1) for f in freq.values())

    # Calculate the denominator: N * (N - 1)
    denominator = N * (N - 1)

    # Compute and return the IC value
    return numerator / denominator


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypt a Caesar cipher, default shift is 3.
    Only processes uppercase letters; other characters remain unchanged.
    """
    plaintext = ""
    for char in ciphertext:
        if char.isupper():
            # Shift the letter by 'shift' positions backward based on the alphabet (A=65 to Z=90)
            new_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext += new_char
        else:
            plaintext += char
    return plaintext


if __name__ == '__main__':
    ciphertext = """\
    WKHUH DUHWZ RZDBV RIFRQ VWUXF WLQJD VRIWZ DUHGH VLJQR QHZDB
    LVWRP DNHLW VRVLP SOHWK DWWKH UHDUH REYLR XVOBQ RGHIL FLHQF
    LHVDQ GWKHR WKHUZ DBLVW RPDNH LWVRF RPSOL FDWHG WKDWW KHUHD
    UHQRR EYLRX VGHIL FLHQF LHVWK HILUV WPHWK RGLVI DUPRU HGLII LFXOW
    """

    # Compute the Index of Coincidence (IC) for the ciphertext
    ic_value = compute_ic(ciphertext)
    print(f"Index of Coincidence (IC) = {ic_value:.4f}")

    # Remove all spaces and newline characters to obtain a continuous ciphertext string
    ciphertext_no_spaces = "".join(ciphertext.split())

    # Decrypt the ciphertext using a Caesar cipher with a shift of 3
    plaintext = decrypt_caesar(ciphertext_no_spaces, shift=3)
    print("\nDecrypted Plaintext:")
    print(plaintext)


'''
We can use the space character to separate the words in the Decrypted plaintext:

THERE ARE TWO WAYS OF CONSTRUCTING SOFTWARE:
ONE IS TO MAKE IT SO SIMPLE THAT THERE ARE OBVIOUSLY NO DEFICIENCIES;
THE OTHER IS TO MAKE IT SO COMPLEX THAT THERE ARE NO OBVIOUS DEFICIENCIES.
'''
