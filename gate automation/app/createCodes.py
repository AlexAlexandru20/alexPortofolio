import random

def find_numbers():
    numbers = []
    for num in range(10000, 100000):
        total = 0
        for n in str(num):
            total += int(n)
        
        if total % 8 == 7:
            numbers.append(num)
    
    return numbers

result = find_numbers()

print(random.choice(result))