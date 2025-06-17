import galois

# 1. 建立 GF(2) 與兩個四次多項式
F2 = galois.GF(2)
f1 = galois.Poly([1, 0, 0, 1, 1], field=F2)      # x⁴ + x + 1
f2 = galois.Poly([1, 1, 0, 0, 1], field=F2)      # x⁴ + x³ + 1

print("Is f1(x) irreducible? ", f1.is_irreducible())
print("Is f2(x) irreducible? ", f2.is_irreducible())

# 2. 以 f1、f2 分別建立 GF(2⁴)
GF1 = galois.GF(2**4, irreducible_poly=f1)
GF2 = galois.GF(2**4, irreducible_poly=f2)

# x 在各擴域中的表示（0b0010 = 2）
x1 = GF1(2)
x2 = GF2(2)

print("Order of x modulo f1(x) =", x1.multiplicative_order())
print("Is f1(x) primitive?     ", x1.multiplicative_order() == 15)
print("Order of x modulo f2(x) =", x2.multiplicative_order())
print("Is f2(x) primitive?     ", x2.multiplicative_order() == 15)

# 3. 列印 x^k (k = 1…15) 在兩個體中的值
print("\nPowers of x modulo f1(x):")
for k in range(1, 16):
    print(f"x^{k} ≡ {x1 ** k}")

print("\nPowers of x modulo f2(x):")
for k in range(1, 16):
    print(f"x^{k} ≡ {x2 ** k}")
