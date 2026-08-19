def swap_elements(arr, i, j):
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp

numbers = [10, 20, 30, 40]
swap_elements(numbers, 1, 3)
print(numbers)
