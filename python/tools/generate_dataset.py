#!/usr/bin/env python3
"""
Generate AICL scripts with AX sub-language actions.

Each script is a complete .aicl spec with Goal/Risk/Recovery/Validation and
Behaviors whose Actions use AX. Every script compiles to real executable code.
"""
from __future__ import annotations
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def make_spec(name, goal, behaviors, risks=None, constraints=None, validations=None):
    lines = [f"# AICL Example: {name}", "# AX sub-language — compiles to real code.", ""]
    lines += ["Goal:", goal, ""]
    if constraints:
        for c in constraints: lines += ["Constraint:", c, ""]
    if risks:
        for risk, recovery in risks: lines += ["Risk:", risk, "Recovery:", recovery, ""]
    lines += ["Layer:", "Core", ""]
    if validations:
        for v in validations: lines += ["Validation:", v, ""]
    for bname, inputs, output, action in behaviors:
        lines += [f"Behavior {bname}", f"    Input: {', '.join(inputs) if inputs else 'input'}",
                  f"    Output: {output}", "    Action:"]
        for aline in action.strip().split('\n'): lines.append(f"        {aline}")
        lines.append("")
    return '\n'.join(lines)

SPECS = []
def add(cat, fn, spec): SPECS.append((cat, fn, spec))

# SORTING
add("sorting","bubble_sort.aicl",make_spec("Bubble Sort","Sort an array using bubble sort",[("Sort",["array"],"array","n = len(array)\nfor i in range(0, n):\n    for j in range(0, n - i - 1):\n        if array[j] > array[j + 1]:\n            array[j], array[j + 1] = array[j + 1], array[j]\nreturn array")],risks=[("Empty array","Return empty array")]))
add("sorting","insertion_sort.aicl",make_spec("Insertion Sort","Sort using insertion sort",[("Sort",["array"],"array","for i in range(1, len(array)):\n    key = array[i]\n    j = i - 1\n    while j >= 0 and array[j] > key:\n        array[j + 1] = array[j]\n        j = j - 1\n    array[j + 1] = key\nreturn array")]))
add("sorting","selection_sort.aicl",make_spec("Selection Sort","Sort using selection sort",[("Sort",["array"],"array","n = len(array)\nfor i in range(0, n):\n    min_idx = i\n    for j in range(i + 1, n):\n        if array[j] < array[min_idx]:\n            min_idx = j\n    array[i], array[min_idx] = array[min_idx], array[i]\nreturn array")]))
add("sorting","quicksort_partition.aicl",make_spec("Quicksort Partition","Lomuto partition",[("Partition",["array","low","high"],"pivot_index","pivot = array[high]\ni = low - 1\nfor j in range(low, high):\n    if array[j] < pivot:\n        i = i + 1\n        array[i], array[j] = array[j], array[i]\narray[i + 1], array[high] = array[high], array[i + 1]\nreturn i + 1")]))
add("sorting","merge_arrays.aicl",make_spec("Merge Sorted Arrays","Merge two sorted arrays",[("Merge",["a","b"],"result","result = []\ni = 0\nj = 0\nwhile i < len(a) and j < len(b):\n    if a[i] <= b[j]:\n        result.append(a[i])\n        i = i + 1\n    else:\n        result.append(b[j])\n        j = j + 1\nwhile i < len(a):\n    result.append(a[i])\n    i = i + 1\nwhile j < len(b):\n    result.append(b[j])\n    j = j + 1\nreturn result")]))
add("sorting","counting_sort.aicl",make_spec("Counting Sort","Sort with counting",[("Sort",["array","max_val"],"result","count = []\nfor i in range(0, max_val + 1):\n    count.append(0)\nfor i in range(0, len(array)):\n    count[array[i]] = count[array[i]] + 1\nresult = []\nfor i in range(0, max_val + 1):\n    for j in range(0, count[i]):\n        result.append(i)\nreturn result")]))

# SEARCHING
add("searching","linear_search.aicl",make_spec("Linear Search","Find target",[("Search",["array","target"],"index","i = 0\nwhile i < len(array):\n    if array[i] == target:\n        return i\n    i = i + 1\nreturn -1")],risks=[("Not found","Return -1")]))
add("searching","binary_search.aicl",make_spec("Binary Search","Search sorted array",[("Search",["array","target"],"index","low = 0\nhigh = len(array) - 1\nwhile low <= high:\n    mid = (low + high) // 2\n    if array[mid] == target:\n        return mid\n    elif array[mid] < target:\n        low = mid + 1\n    else:\n        high = mid - 1\nreturn -1")],constraints=["Array must be sorted"]))
add("searching","find_max.aicl",make_spec("Find Maximum","Max value",[("FindMax",["array"],"maximum","maximum = array[0]\nfor i in range(1, len(array)):\n    if array[i] > maximum:\n        maximum = array[i]\nreturn maximum")]))
add("searching","find_min.aicl",make_spec("Find Minimum","Min value",[("FindMin",["array"],"minimum","minimum = array[0]\nfor i in range(1, len(array)):\n    if array[i] < minimum:\n        minimum = array[i]\nreturn minimum")]))
add("searching","find_second_largest.aicl",make_spec("Second Largest","2nd largest",[("FindSecond",["array"],"second","largest = array[0]\nsecond = array[0]\nfor i in range(1, len(array)):\n    if array[i] > largest:\n        second = largest\n        largest = array[i]\n    elif array[i] > second:\n        second = array[i]\nreturn second")]))

# MATH
add("math","factorial_iterative.aicl",make_spec("Factorial Iterative","Compute factorial",[("Compute",["n"],"result","result = 1\nfor i in range(1, n + 1):\n    result = result * i\nreturn result")]))
add("math","factorial_recursive.aicl",make_spec("Factorial Recursive","Recursive",[("Compute",["n"],"result","if n <= 1:\n    return 1\nreturn n * compute(n - 1)")]))
add("math","fibonacci_iterative.aicl",make_spec("Fibonacci Iterative","nth Fibonacci",[("Compute",["n"],"result","if n <= 1:\n    return n\nprev = 0\ncurr = 1\nfor i in range(2, n):\n    next = prev + curr\n    prev = curr\n    curr = next\nreturn curr")]))
add("math","gcd_euclid.aicl",make_spec("GCD Euclid","GCD",[("Compute",["a","b"],"result","while b != 0:\n    temp = b\n    b = a % b\n    a = temp\nreturn a")]))
add("math","is_prime.aicl",make_spec("Prime Check","Is prime",[("Check",["n"],"result","if n < 2:\n    return false\ni = 2\nwhile i * i <= n:\n    if n % i == 0:\n        return false\n    i = i + 1\nreturn true")]))
add("math","power_iterative.aicl",make_spec("Power Iterative","base^exp",[("Compute",["base","exponent"],"result","result = 1\nwhile exponent > 0:\n    result = result * base\n    exponent = exponent - 1\nreturn result")]))
add("math","digit_sum.aicl",make_spec("Digit Sum","Sum digits",[("Compute",["n"],"total","total = 0\nwhile n > 0:\n    total = total + (n % 10)\n    n = n // 10\nreturn total")]))
add("math","collatz_steps.aicl",make_spec("Collatz Steps","Steps to 1",[("Steps",["n"],"count","count = 0\nwhile n != 1:\n    if n % 2 == 0:\n        n = n // 2\n    else:\n        n = 3 * n + 1\n    count = count + 1\nreturn count")]))
add("math","is_power_of_two.aicl",make_spec("Power of Two","Is 2^k",[("Check",["n"],"result","if n <= 0:\n    return false\nwhile n % 2 == 0:\n    n = n // 2\nreturn n == 1")]))
add("math","sum_range.aicl",make_spec("Sum Range","0+1+...+(n-1)",[("Sum",["n"],"total","total = 0\nfor i in range(0, n):\n    total = total + i\nreturn total")]))
add("math","multiply_table.aicl",make_spec("Multiplication Table","n*n",[("Build",["n"],"table","table = []\nfor i in range(1, n + 1):\n    for j in range(1, n + 1):\n        table.append(i * j)\nreturn table")]))
add("math","count_down.aicl",make_spec("Count Down","n to 1",[("Build",["n"],"result","result = []\nwhile n > 0:\n    result.append(n)\n    n = n - 1\nreturn result")]))
add("math","absolute_value.aicl",make_spec("Absolute Value","abs(n)",[("Abs",["n"],"result","if n < 0:\n    return -n\nreturn n")]))
add("math","clamp.aicl",make_spec("Clamp","Clamp value",[("Clamp",["value","low","high"],"result","if value < low:\n    return low\nelif value > high:\n    return high\nreturn value")]))

# STRINGS
add("strings","string_length.aicl",make_spec("String Length","Count chars",[("Count",["text"],"count","count = 0\nfor ch in text:\n    count = count + 1\nreturn count")]))
add("strings","count_vowels.aicl",make_spec("Count Vowels","Vowel count",[("Count",["text"],"count","count = 0\nfor ch in text:\n    if ch == \"a\":\n        count = count + 1\n    elif ch == \"e\":\n        count = count + 1\n    elif ch == \"i\":\n        count = count + 1\n    elif ch == \"o\":\n        count = count + 1\n    elif ch == \"u\":\n        count = count + 1\nreturn count")]))
add("strings","palindrome_check.aicl",make_spec("Palindrome","Is palindrome",[("Check",["text"],"result","left = 0\nright = len(text) - 1\nwhile left < right:\n    if text[left] != text[right]:\n        return false\n    left = left + 1\n    right = right - 1\nreturn true")]))
add("strings","reverse_string.aicl",make_spec("Reverse String","Reverse",[("Reverse",["text"],"result","result = \"\"\ni = len(text) - 1\nwhile i >= 0:\n    result = result + text[i]\n    i = i - 1\nreturn result")]))

# ARRAYS
add("arrays","sum_array.aicl",make_spec("Sum Array","Sum elements",[("Sum",["array"],"total","total = 0\nfor i in range(0, len(array)):\n    total = total + array[i]\nreturn total")]))
add("arrays","reverse_array.aicl",make_spec("Reverse Array","Reverse in place",[("Reverse",["array"],"array","left = 0\nright = len(array) - 1\nwhile left < right:\n    array[left], array[right] = array[right], array[left]\n    left = left + 1\n    right = right - 1\nreturn array")]))
add("arrays","count_occurrences.aicl",make_spec("Count Occurrences","Count value",[("Count",["array","value"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] == value:\n        count = count + 1\nreturn count")]))
add("arrays","filter_greater.aicl",make_spec("Filter Greater","Above threshold",[("Filter",["array","threshold"],"result","result = []\nfor i in range(0, len(array)):\n    if array[i] > threshold:\n        result.append(array[i])\nreturn result")]))
add("arrays","array_equal.aicl",make_spec("Array Equal","Compare",[("Compare",["a","b"],"result","if len(a) != len(b):\n    return false\nfor i in range(0, len(a)):\n    if a[i] != b[i]:\n        return false\nreturn true")]))
add("arrays","max_subarray_sum.aicl",make_spec("Max Subarray","Kadane",[("MaxSub",["array"],"max_sum","max_sum = array[0]\ncurr_sum = array[0]\nfor i in range(1, len(array)):\n    if curr_sum + array[i] > array[i]:\n        curr_sum = curr_sum + array[i]\n    else:\n        curr_sum = array[i]\n    if curr_sum > max_sum:\n        max_sum = curr_sum\nreturn max_sum")]))
add("arrays","rotate_array.aicl",make_spec("Rotate Array","Right by k",[("Rotate",["array","k"],"result","n = len(array)\nresult = []\nfor i in range(0, n):\n    src = (i + n - k) % n\n    result.append(array[src])\nreturn result")]))

# BITOPS
add("bitops","count_set_bits.aicl",make_spec("Count Set Bits","Popcount",[("Count",["n"],"count","count = 0\nwhile n > 0:\n    count = count + (n % 2)\n    n = n // 2\nreturn count")]))
add("bitops","is_odd.aicl",make_spec("Is Odd","n odd",[("Check",["n"],"result","if n % 2 == 0:\n    return false\nreturn true")]))
add("bitops","is_even.aicl",make_spec("Is Even","n even",[("Check",["n"],"result","if n % 2 == 0:\n    return true\nreturn false")]))

# RECURSION
add("recursion","fibonacci_recursive.aicl",make_spec("Fibonacci Recursive","Recursive",[("Fib",["n"],"result","if n <= 1:\n    return n\nreturn fib(n - 1) + fib(n - 2)")]))
add("recursion","sum_digits_recursive.aicl",make_spec("Sum Digits Recursive","Recursive",[("Sum",["n"],"total","if n == 0:\n    return 0\nreturn (n % 10) + sum(n // 10)")]))
add("recursion","power_recursive.aicl",make_spec("Power Recursive","Recursive",[("Power",["base","exp"],"result","if exp == 0:\n    return 1\nreturn base * power(base, exp - 1)")]))

# LOGIC
add("logic","median_of_three.aicl",make_spec("Median of Three","Median",[("Median",["a","b","c"],"result","if a > b:\n    if a < c:\n        return a\n    elif b > c:\n        return b\n    return c\nelse:\n    if a > c:\n        return a\n    elif b < c:\n        return b\n    return c")]))
add("logic","max_of_three.aicl",make_spec("Max of Three","Maximum",[("Max",["a","b","c"],"result","maximum = a\nif b > maximum:\n    maximum = b\nif c > maximum:\n    maximum = c\nreturn maximum")]))
add("logic","grade_letter.aicl",make_spec("Grade Letter","Score to grade",[("Grade",["score"],"grade","if score >= 90:\n    return \"A\"\nelif score >= 80:\n    return \"B\"\nelif score >= 70:\n    return \"C\"\nelif score >= 60:\n    return \"D\"\nreturn \"F\"")]))
add("logic","leap_year.aicl",make_spec("Leap Year","Is leap",[("Check",["year"],"result","if year % 400 == 0:\n    return true\nif year % 100 == 0:\n    return false\nif year % 4 == 0:\n    return true\nreturn false")]))
add("logic","sign_function.aicl",make_spec("Sign Function","sign(n)",[("Sign",["n"],"result","if n < 0:\n    return -1\nif n == 0:\n    return 0\nreturn 1")]))
add("logic","traffic_light.aicl",make_spec("Traffic Light","Action",[("Action",["color"],"result","if color == \"red\":\n    return \"stop\"\nelif color == \"yellow\":\n    return \"slow\"\nelif color == \"green\":\n    return \"go\"\nreturn \"invalid\"")]))
add("logic","quadrant.aicl",make_spec("Quadrant","Quad of point",[("Find",["x","y"],"quadrant","if x == 0 or y == 0:\n    return 0\nif x > 0:\n    if y > 0:\n        return 1\n    return 4\nif y > 0:\n    return 2\nreturn 3")]))

# CONVERSIONS
add("conversions","celsius_to_fahrenheit.aicl",make_spec("C to F","Convert",[("Convert",["celsius"],"fahrenheit","return (celsius * 9) // 5 + 32")]))
add("conversions","fahrenheit_to_celsius.aicl",make_spec("F to C","Convert",[("Convert",["fahrenheit"],"celsius","return (fahrenheit - 32) * 5 // 9")]))
add("conversions","minutes_to_seconds.aicl",make_spec("Minutes to Seconds","Convert",[("Convert",["minutes"],"seconds","return minutes * 60")]))

# NUMBER THEORY
add("numbertheory","sum_divisors.aicl",make_spec("Sum Divisors","Proper divisors",[("Sum",["n"],"total","total = 0\ni = 1\nwhile i * i <= n:\n    if n % i == 0:\n        total = total + i\n        if i != n // i:\n            total = total + (n // i)\n    i = i + 1\nreturn total - n")]))
add("numbertheory","lcm.aicl",make_spec("LCM","Least common multiple",[("Compute",["a","b"],"result","if a == 0 or b == 0:\n    return 0\nx = a\ny = b\nwhile y != 0:\n    temp = y\n    y = x % y\n    x = temp\nreturn (a // x) * b")]))

# GEOMETRY
add("geometry","rectangle_area.aicl",make_spec("Rectangle Area","w*h",[("Area",["width","height"],"area","return width * height")]))
add("geometry","triangle_area.aicl",make_spec("Triangle Area","b*h/2",[("Area",["base","height"],"area","return (base * height) // 2")]))
add("geometry","distance_squared.aicl",make_spec("Distance Squared","dx^2+dy^2",[("Distance",["x1","y1","x2","y2"],"result","dx = x2 - x1\ndy = y2 - y1\nreturn dx * dx + dy * dy")]))

# STATISTICS
add("statistics","average.aicl",make_spec("Average","Mean",[("Average",["array"],"mean","if len(array) == 0:\n    return 0\ntotal = 0\nfor i in range(0, len(array)):\n    total = total + array[i]\nreturn total // len(array)")]))
add("statistics","range_value.aicl",make_spec("Range","max-min",[("Range",["array"],"range_val","minimum = array[0]\nmaximum = array[0]\nfor i in range(1, len(array)):\n    if array[i] < minimum:\n        minimum = array[i]\n    if array[i] > maximum:\n        maximum = array[i]\nreturn maximum - minimum")]))
add("statistics","median_sorted.aicl",make_spec("Median Sorted","Median",[("Median",["array"],"median","n = len(array)\nif n == 0:\n    return 0\nif n % 2 == 1:\n    return array[n // 2]\nreturn (array[n // 2 - 1] + array[n // 2]) // 2")]))

# GAMES
add("games","rock_paper_scissors.aicl",make_spec("Rock Paper Scissors","Winner",[("Winner",["p1","p2"],"result","if p1 == p2:\n    return \"draw\"\nif p1 == \"rock\":\n    if p2 == \"scissors\":\n        return \"p1\"\n    return \"p2\"\nif p1 == \"paper\":\n    if p2 == \"rock\":\n        return \"p1\"\n    return \"p2\"\nif p2 == \"paper\":\n    return \"p1\"\nreturn \"p2\"")]))
add("games","guess_feedback.aicl",make_spec("Guess Feedback","Compare",[("Compare",["guess","target"],"result","if guess == target:\n    return \"correct\"\nif guess < target:\n    return \"too low\"\nreturn \"too high\"")]))
add("games","dice_roll.aicl",make_spec("Dice Roll","Seeded",[("Roll",["seed"],"value","return (seed % 6) + 1")]))

# VALIDATION
add("validation","is_positive.aicl",make_spec("Is Positive","n > 0",[("Check",["n"],"result","if n > 0:\n    return true\nreturn false")]))
add("validation","is_in_range.aicl",make_spec("Is in Range","Within bounds",[("Check",["value","low","high"],"result","if value < low:\n    return false\nif value > high:\n    return false\nreturn true")]))
add("validation","password_strength.aicl",make_spec("Password Strength","Score",[("Strength",["password"],"score","length = 0\nfor ch in password:\n    length = length + 1\nif length < 6:\n    return 0\nif length < 10:\n    return 1\nif length < 14:\n    return 2\nreturn 3")]))
add("validation","validate_age.aicl",make_spec("Validate Age","0-150",[("Validate",["age"],"result","if age < 0:\n    return false\nif age > 150:\n    return false\nreturn true")]))


# ═══ MORE MATH ═══
add("math","triangular_number.aicl",make_spec("Triangular Number","n*(n+1)/2",[("Compute",["n"],"result","return n * (n + 1) // 2")]))
add("math","square_number.aicl",make_spec("Square","n squared",[("Compute",["n"],"result","return n * n")]))
add("math","cube_number.aicl",make_spec("Cube","n cubed",[("Compute",["n"],"result","return n * n * n")]))
add("math","double.aicl",make_spec("Double","2*n",[("Double",["n"],"result","return n * 2")]))
add("math","halve_integer.aicl",make_spec("Halve","n//2",[("Halve",["n"],"result","return n // 2")]))
add("math","negate.aicl",make_spec("Negate","-n",[("Negate",["n"],"result","return -n")]))
add("math","increment.aicl",make_spec("Increment","n+1",[("Increment",["n"],"result","return n + 1")]))
add("math","decrement.aicl",make_spec("Decrement","n-1",[("Decrement",["n"],"result","return n - 1")]))
add("math","square_root_floor.aicl",make_spec("Square Root Floor","floor(sqrt(n))",[("Compute",["n"],"result","if n < 2:\n    return n\nr = 0\nbit = 1\nwhile bit <= n:\n    bit = bit * 4\nwhile bit > 0:\n    if n >= r + bit:\n        n = n - (r + bit)\n        r = r // 2 + bit\n    else:\n        r = r // 2\n    bit = bit // 4\nreturn r")]))
add("math","cube_root_floor.aicl",make_spec("Cube Root Floor","floor(cbrt(n))",[("Compute",["n"],"result","r = 0\nwhile (r + 1) * (r + 1) * (r + 1) <= n:\n    r = r + 1\nreturn r")]))
add("math","sum_squares.aicl",make_spec("Sum of Squares","1^2+2^2+...+n^2",[("Sum",["n"],"total","total = 0\nfor i in range(1, n + 1):\n    total = total + i * i\nreturn total")]))
add("math","sum_cubes.aicl",make_spec("Sum of Cubes","1^3+...+n^3",[("Sum",["n"],"total","total = 0\nfor i in range(1, n + 1):\n    total = total + i * i * i\nreturn total")]))
add("math","modulo.aicl",make_spec("Modulo","a mod b",[("Mod",["a","b"],"result","return a % b")]))
add("math","integer_division.aicl",make_spec("Integer Division","a // b",[("Div",["a","b"],"result","return a // b")]))
add("math","power_of_ten_check.aicl",make_spec("Power of Ten","Is 10^k",[("Check",["n"],"result","if n <= 0:\n    return false\nwhile n > 1:\n    if n % 10 != 0:\n        return false\n    n = n // 10\nreturn true")]))
add("math","reverse_digits.aicl",make_spec("Reverse Digits","Reverse decimal",[("Reverse",["n"],"result","result = 0\nwhile n > 0:\n    result = result * 10 + (n % 10)\n    n = n // 10\nreturn result")]))
add("math","count_digits.aicl",make_spec("Count Digits","Number of digits",[("Count",["n"],"count","if n == 0:\n    return 1\ncount = 0\nwhile n > 0:\n    count = count + 1\n    n = n // 10\nreturn count")]))

# ═══ MORE ARRAYS ═══
add("arrays","array_min_index.aicl",make_spec("Min Index","Index of min",[("FindMinIdx",["array"],"index","index = 0\nfor i in range(1, len(array)):\n    if array[i] < array[index]:\n        index = i\nreturn index")]))
add("arrays","array_max_index.aicl",make_spec("Max Index","Index of max",[("FindMaxIdx",["array"],"index","index = 0\nfor i in range(1, len(array)):\n    if array[i] > array[index]:\n        index = i\nreturn index")]))
add("arrays","array_product.aicl",make_spec("Array Product","Product of elements",[("Product",["array"],"product","product = 1\nfor i in range(0, len(array)):\n    product = product * array[i]\nreturn product")]))
add("arrays","build_range_array.aicl",make_spec("Build Range","0..n-1 as array",[("Build",["n"],"result","result = []\nfor i in range(0, n):\n    result.append(i)\nreturn result")]))
add("arrays","build_squares.aicl",make_spec("Build Squares","Squares 0..n-1",[("Build",["n"],"result","result = []\nfor i in range(0, n):\n    result.append(i * i)\nreturn result")]))
add("arrays","contains_value.aicl",make_spec("Contains","Has value",[("Contains",["array","value"],"result","for i in range(0, len(array)):\n    if array[i] == value:\n        return true\nreturn false")]))
add("arrays","find_first_even.aicl",make_spec("First Even","First even element",[("Find",["array"],"result","for i in range(0, len(array)):\n    if array[i] % 2 == 0:\n        return array[i]\nreturn -1")]))
add("arrays","find_first_odd.aicl",make_spec("First Odd","First odd element",[("Find",["array"],"result","for i in range(0, len(array)):\n    if array[i] % 2 != 0:\n        return array[i]\nreturn -1")]))
add("arrays","count_even.aicl",make_spec("Count Even","Even count",[("Count",["array"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] % 2 == 0:\n        count = count + 1\nreturn count")]))
add("arrays","count_odd.aicl",make_spec("Count Odd","Odd count",[("Count",["array"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] % 2 != 0:\n        count = count + 1\nreturn count")]))
add("arrays","sum_even.aicl",make_spec("Sum Even","Sum of even",[("Sum",["array"],"total","total = 0\nfor i in range(0, len(array)):\n    if array[i] % 2 == 0:\n        total = total + array[i]\nreturn total")]))
add("arrays","sum_odd.aicl",make_spec("Sum Odd","Sum of odd",[("Sum",["array"],"total","total = 0\nfor i in range(0, len(array)):\n    if array[i] % 2 != 0:\n        total = total + array[i]\nreturn total")]))
add("arrays","scale_array.aicl",make_spec("Scale Array","Multiply each by k",[("Scale",["array","k"],"result","result = []\nfor i in range(0, len(array)):\n    result.append(array[i] * k)\nreturn result")]))
add("arrays","shift_array.aicl",make_spec("Shift Array","Add k to each",[("Shift",["array","k"],"result","result = []\nfor i in range(0, len(array)):\n    result.append(array[i] + k)\nreturn result")]))
add("arrays","all_positive.aicl",make_spec("All Positive","Every element > 0",[("Check",["array"],"result","for i in range(0, len(array)):\n    if array[i] <= 0:\n        return false\nreturn true")]))
add("arrays","any_negative.aicl",make_spec("Any Negative","Has element < 0",[("Check",["array"],"result","for i in range(0, len(array)):\n    if array[i] < 0:\n        return true\nreturn false")]))
add("arrays","max_diff.aicl",make_spec("Max Difference","max adjacent diff",[("MaxDiff",["array"],"result","result = 0\nfor i in range(1, len(array)):\n    diff = array[i] - array[i - 1]\n    if diff < 0:\n        diff = -diff\n    if diff > result:\n        result = diff\nreturn result")]))

# ═══ MORE STRINGS ═══
add("strings","count_consonants.aicl",make_spec("Count Consonants","Non-vowel letters",[("Count",["text"],"count","count = 0\nfor ch in text:\n    if ch != \"a\" and ch != \"e\" and ch != \"i\" and ch != \"o\" and ch != \"u\":\n        count = count + 1\nreturn count")]))
add("strings","count_spaces.aicl",make_spec("Count Spaces","Space count",[("Count",["text"],"count","count = 0\nfor ch in text:\n    if ch == \" \":\n        count = count + 1\nreturn count")]))
add("strings","first_char.aicl",make_spec("First Character","text[0]",[("First",["text"],"result","if len(text) == 0:\n    return \"\"\nreturn text[0]")]))

# ═══ MORE LOGIC ═══
add("logic","min_of_three.aicl",make_spec("Min of Three","Minimum",[("Min",["a","b","c"],"result","minimum = a\nif b < minimum:\n    minimum = b\nif c < minimum:\n    minimum = c\nreturn minimum")]))
add("logic","all_equal.aicl",make_spec("All Equal","a==b==c",[("Check",["a","b","c"],"result","if a == b:\n    if b == c:\n        return true\nreturn false")]))
add("logic","any_equal.aicl",make_spec("Any Equal","Any pair equal",[("Check",["a","b","c"],"result","if a == b:\n    return true\nif b == c:\n    return true\nif a == c:\n    return true\nreturn false")]))
add("logic","between.aicl",make_spec("Between","Is x between a and b",[("Check",["x","a","b"],"result","if x >= a:\n    if x <= b:\n        return true\nreturn false")]))
add("logic","strictly_between.aicl",make_spec("Strictly Between","a < x < b",[("Check",["x","a","b"],"result","if x > a:\n    if x < b:\n        return true\nreturn false")]))
add("logic","ascending_order.aicl",make_spec("Ascending","a <= b <= c",[("Check",["a","b","c"],"result","if a <= b:\n    if b <= c:\n        return true\nreturn false")]))
add("logic","descending_order.aicl",make_spec("Descending","a >= b >= c",[("Check",["a","b","c"],"result","if a >= b:\n    if b >= c:\n        return true\nreturn false")]))
add("logic","is_adult.aicl",make_spec("Is Adult","age >= 18",[("Check",["age"],"result","if age >= 18:\n    return true\nreturn false")]))
add("logic","is_weekend.aicl",make_spec("Is Weekend","Day 6 or 7",[("Check",["day"],"result","if day == 6:\n    return true\nif day == 7:\n    return true\nreturn false")]))
add("logic","season_from_month.aicl",make_spec("Season","Month to season",[("Season",["month"],"result","if month >= 3:\n    if month <= 5:\n        return \"spring\"\nif month >= 6:\n    if month <= 8:\n        return \"summer\"\nif month >= 9:\n    if month <= 11:\n        return \"autumn\"\nreturn \"winter\"")]))

# ═══ MORE CONVERSIONS ═══
add("conversions","hours_to_minutes.aicl",make_spec("Hours to Minutes","Convert",[("Convert",["hours"],"minutes","return hours * 60")]))
add("conversions","days_to_hours.aicl",make_spec("Days to Hours","Convert",[("Convert",["days"],"hours","return days * 24")]))
add("conversions","weeks_to_days.aicl",make_spec("Weeks to Days","Convert",[("Convert",["weeks"],"days","return weeks * 7")]))
add("conversions","meters_to_cm.aicl",make_spec("Meters to cm","Convert",[("Convert",["meters"],"cm","return meters * 100")]))
add("conversions","kg_to_grams.aicl",make_spec("Kg to Grams","Convert",[("Convert",["kg"],"grams","return kg * 1000")]))

# ═══ MORE GAMES ═══
add("games","coin_toss.aicl",make_spec("Coin Toss","Heads or tails",[("Toss",["seed"],"result","if seed % 2 == 0:\n    return \"heads\"\nreturn \"tails\"")]))
add("games","card_value.aicl",make_spec("Card Value","Face card to value",[("Value",["card"],"result","if card == \"A\":\n    return 1\nif card == \"J\":\n    return 11\nif card == \"Q\":\n    return 12\nif card == \"K\":\n    return 13\nreturn card")]))
add("games","winner_by_score.aicl",make_spec("Winner by Score","Higher score wins",[("Winner",["p1_score","p2_score"],"result","if p1_score > p2_score:\n    return \"p1\"\nif p2_score > p1_score:\n    return \"p2\"\nreturn \"draw\"")]))

# ═══ MORE NUMBER THEORY ═══
add("numbertheory","next_prime.aicl",make_spec("Next Prime","Smallest prime > n",[("Find",["n"],"result","candidate = n + 1\nwhile true:\n    is_p = true\nd = 2\nwhile d * d <= candidate:\n    if candidate % d == 0:\n        is_p = false\nd = d + 1\nif is_p:\n    return candidate\ncandidate = candidate + 1")]))
add("numbertheory","is_armstrong.aicl",make_spec("Armstrong Number","n == sum of cubes of digits",[("Check",["n"],"result","original = n\ntotal = 0\nwhile n > 0:\n    digit = n % 10\ntotal = total + digit * digit * digit\nn = n // 10\nreturn total == original")]))
add("numbertheory","reverse_number.aicl",make_spec("Reverse Number","Decimal reversal",[("Reverse",["n"],"result","result = 0\nwhile n > 0:\n    result = result * 10 + (n % 10)\nn = n // 10\nreturn result")]))

# ═══ MORE GEOMETRY ═══
add("geometry","perimeter_rectangle.aicl",make_spec("Rectangle Perimeter","2*(w+h)",[("Perimeter",["width","height"],"perimeter","return 2 * (width + height)")]))
add("geometry","perimeter_square.aicl",make_spec("Square Perimeter","4*side",[("Perimeter",["side"],"perimeter","return 4 * side")]))
add("geometry","cube_volume.aicl",make_spec("Cube Volume","side^3",[("Volume",["side"],"volume","return side * side * side")]))
add("geometry","box_volume.aicl",make_spec("Box Volume","w*h*d",[("Volume",["width","height","depth"],"volume","return width * height * depth")]))
add("geometry","circle_circumference.aicl",make_spec("Circle Circumference","2*pi*r approx",[("Circumference",["radius"],"circumference","return 2 * radius * 314 // 100")]))

# ═══ MORE STATISTICS ═══
add("statistics","sum_squares_array.aicl",make_spec("Sum of Squares Array","Sum of squared elements",[("Sum",["array"],"total","total = 0\nfor i in range(0, len(array)):\n    total = total + array[i] * array[i]\nreturn total")]))
add("statistics","product_array.aicl",make_spec("Array Product","Product of elements",[("Product",["array"],"product","product = 1\nfor i in range(0, len(array)):\n    product = product * array[i]\nreturn product")]))
add("statistics","count_positive.aicl",make_spec("Count Positive","Positive count",[("Count",["array"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] > 0:\n        count = count + 1\nreturn count")]))
add("statistics","count_negative.aicl",make_spec("Count Negative","Negative count",[("Count",["array"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] < 0:\n        count = count + 1\nreturn count")]))
add("statistics","count_zero.aicl",make_spec("Count Zeros","Zero count",[("Count",["array"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] == 0:\n        count = count + 1\nreturn count")]))

# ═══ MORE VALIDATION ═══
add("validation","is_negative.aicl",make_spec("Is Negative","n < 0",[("Check",["n"],"result","if n < 0:\n    return true\nreturn false")]))
add("validation","is_zero.aicl",make_spec("Is Zero","n == 0",[("Check",["n"],"result","if n == 0:\n    return true\nreturn false")]))
add("validation","is_nonzero.aicl",make_spec("Is Nonzero","n != 0",[("Check",["n"],"result","if n == 0:\n    return false\nreturn true")]))
add("validation","validate_score.aicl",make_spec("Validate Score","0-100",[("Validate",["score"],"result","if score < 0:\n    return false\nif score > 100:\n    return false\nreturn true")]))
add("validation","validate_month.aicl",make_spec("Validate Month","1-12",[("Validate",["month"],"result","if month < 1:\n    return false\nif month > 12:\n    return false\nreturn true")]))
add("validation","validate_day.aicl",make_spec("Validate Day","1-31",[("Validate",["day"],"result","if day < 1:\n    return false\nif day > 31:\n    return false\nreturn true")]))
add("validation","validate_hour.aicl",make_spec("Validate Hour","0-23",[("Validate",["hour"],"result","if hour < 0:\n    return false\nif hour > 23:\n    return false\nreturn true")]))
add("validation","validate_minute.aicl",make_spec("Validate Minute","0-59",[("Validate",["minute"],"result","if minute < 0:\n    return false\nif minute > 59:\n    return false\nreturn true")]))

# ═══ MORE SEARCHING ═══
add("searching","find_first_positive.aicl",make_spec("First Positive","First positive elem",[("Find",["array"],"result","for i in range(0, len(array)):\n    if array[i] > 0:\n        return array[i]\nreturn 0")]))
add("searching","find_last_even.aicl",make_spec("Last Even","Last even elem",[("Find",["array"],"result","result = -1\nfor i in range(0, len(array)):\n    if array[i] % 2 == 0:\n        result = array[i]\nreturn result")]))
add("searching","count_target.aicl",make_spec("Count Target","Occurrences of target",[("Count",["array","target"],"count","count = 0\nfor i in range(0, len(array)):\n    if array[i] == target:\n        count = count + 1\nreturn count")]))

# ═══ FINAL BATCH to reach 150+ ═══
add("math","percentage.aicl",make_spec("Percentage","part/total*100",[("Compute",["part","total"],"result","if total == 0:\n    return 0\nreturn part * 100 // total")]))
add("math","average_of_two.aicl",make_spec("Average of Two","(a+b)/2",[("Avg",["a","b"],"result","return (a + b) // 2")]))
add("arrays","swap_first_last.aicl",make_spec("Swap First Last","Swap first and last element",[("Swap",["array"],"array","n = len(array)\nif n < 2:\n    return array\ntemp = array[0]\narray[0] = array[n - 1]\narray[n - 1] = temp\nreturn array")]))
add("logic","is_multiple.aicl",make_spec("Is Multiple","Is a a multiple of b",[("Check",["a","b"],"result","if b == 0:\n    return false\nreturn a % b == 0")]))
add("logic","is_divisor.aicl",make_spec("Is Divisor","Does b divide a",[("Check",["a","b"],"result","if b == 0:\n    return false\nif a % b == 0:\n    return true\nreturn false")]))


def main():
    p = argparse.ArgumentParser(description="Generate AICL scripts with AX.")
    p.add_argument("--out", default="aicl_dataset")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    cats = {}
    for cat, fn, spec in SPECS:
        d = os.path.join(args.out, cat); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, fn), 'w', encoding='utf-8') as f: f.write(spec)
        cats.setdefault(cat, []).append(fn)
    corpus = '\n'.join(f"### AICL DATASET: {c}/{f}\n=== SPEC ===\n{s.rstrip()}\n"
                       for c, f, s in SPECS)
    cp = os.path.join(args.out, "aicl_dataset_corpus.raw")
    with open(cp, 'w', encoding='utf-8') as f: f.write(corpus)
    print(f"\n[done] {len(SPECS)} scripts in {args.out}/")
    for c, fs in sorted(cats.items()): print(f"  {c:20s}: {len(fs):3d}")
    print(f"\n  Corpus: {cp} ({len(corpus):,} chars)")


if __name__ == "__main__":
    main()
