import random

logfile = open('./logfile.txt', 'w+')

numbers = [int(input("Enter number: ")) for _ in range(6)]
wanted_result = int(input("Enter the result: "))

logfile.write(f"{numbers}\n")
logfile.write(f"{wanted_result}\n\n")

# Define the function blocks
def addition(x, y):
    return x + y, f"{x} + {y} = {x + y}\n"

def subtraction(x, y):
    return x - y, f"{x} - {y} = {x - y}\n"

def multiplication(x, y):
    return x * y, f"{x} * {y} = {x * y}\n"

def division(x, y):
    if y != 0 and x % y == 0:
        return x / y, f"{x} / {y} = {x / y}\n"
    else:
        return options[random.randint(0, 2)](x, y)

# Map the inputs to the function blocks
options = {
    0: addition,
    1: subtraction,
    2: multiplication,
    3: division,
}

log_results = []

def do_math(numbers_input):
    test_numbers = numbers_input.copy()
    random.shuffle(test_numbers)
    log_results.clear()

    while len(test_numbers) > 1:
        results = options[random.randint(0, 3)](test_numbers.pop(), test_numbers.pop())
        test_numbers.append(results[0])
        log_results.append(results[1])

    result = int(test_numbers[0])
    if result == wanted_result:
        logfile.writelines(log_results)
        logfile.write(f"\nResult: {result}\n")
    return result

current_result = 0
while current_result != wanted_result:
    current_result = do_math(numbers)

print('----------------------\n')
print("".join(log_results))
print(f"Result: {current_result}")
logfile.close()
