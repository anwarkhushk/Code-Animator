import numpy as np
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])
mean_x = np.mean(x)
mean_y = np.mean(y)
numerator = np.sum((x - mean_x) * (y - mean_y))
denominator = np.sum((x - mean_x) ** 2)

b = numerator / denominator
a = mean_y - b * mean_x
print("Intercept (a):", a)
print("Slope (b):", b)
print(f"Regression Line: y = {a:.2f} + {b:.2f}x")
