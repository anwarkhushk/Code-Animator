def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

x = factorial(3)
print(x)
