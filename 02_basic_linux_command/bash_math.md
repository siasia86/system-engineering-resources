# Bash Math Operations Guide

*Content was rephrased for compliance with licensing restrictions*

Source: [phoenixNAP - Bash Math Operations](https://phoenixnap.com/kb/bash-math)

## Overview

Bash scripting supports mathematical operations for automation tasks like unit conversions, temperature calculations, and basic arithmetic. This guide covers various methods to perform calculations in Bash.

## Common Use Cases

- Basic arithmetic (addition, subtraction, multiplication, division)
- Number incrementing and decrementing
- Unit conversions
- Floating-point calculations
- Percentage calculations
- Working with different number bases (binary, octal, hexadecimal)

## Methods for Bash Math

### 1. Arithmetic Expansion (Recommended)

The preferred method using shell arithmetic expansion:

```bash
$((expression))
```

Example:
```bash
echo $((2+3))  # Output: 5
```

### 2. awk Command

Pattern selector that can perform calculations:

```bash
awk 'BEGIN { x = 2; y = 3; print "x + y = "(x+y) }'
```

### 3. bc Command

Basic calculator utility for arbitrary precision arithmetic:

```bash
echo "2+3" | bc
```

### 4. dc Command

Desk calculator supporting reverse Polish notation:

```bash
echo "2 3 + p" | dc
```

### 5. declare Command

Integer calculations with the `-i` option:

```bash
declare -i x=2 y=3 z=x+y
echo $x + $y = $z
```

### 6. expr Command

Legacy utility for integer arithmetic:

```bash
expr 2 + 3
```

### 7. let Command

Built-in command for arithmetic operations:

```bash
let x=2+3
echo $x
```

### 8. test Command

Evaluates conditional expressions:

```bash
test 2 -gt 3; echo $?
# or
[ 2 -gt 3 ]; echo $?
```

## Arithmetic Operators

| Operator | Description |
|----------|-------------|
| `++x`, `x++` | Pre and post-increment |
| `--x`, `x--` | Pre and post-decrement |
| `+`, `-`, `*`, `/` | Addition, subtraction, multiplication, division |
| `%` | Modulo (remainder) |
| `**` or `^` | Exponentiation |
| `&&`, `||`, `!` | Logical AND, OR, negation |
| `&`, `|`, `^`, `~` | Bitwise operations |
| `<=`, `<`, `>`, `>=` | Comparison operators |
| `==`, `!=` | Equality operators |
| `=` | Assignment operator |

## Practical Examples

### Integer Math

```bash
echo $((x=2, y=3, x+y))  # Output: 5

# Multiple calculations
((x=2, y=3, a=x+y, b=x*y, c=x**y))
echo $a, $b, $c  # Output: 5, 6, 8
```

### Incrementing/Decrementing

Pre-increment (increment before use):
```bash
number=1
echo $((++number))  # Output: 2
```

Post-increment (increment after use):
```bash
number=1
echo $((number++))  # Output: 1
echo $number        # Output: 2
```

### Floating-Point Arithmetic

Bash arithmetic expansion doesn't support floating-point. Use alternatives:

**Using awk:**
```bash
awk 'BEGIN { x = 2.3; y = 3.2; print "x * y = "(x * y) }'
```

**Using bc:**
```bash
echo "2.3 * 3.2" | bc -l
```

**Using Perl:**
```bash
perl -e 'print 2.3*3.2'
```

### Percentage Calculation

**Using printf:**
```bash
printf %.2f%% "$((10**4 * 40/71))e-4"%
```

**Using awk:**
```bash
awk 'BEGIN { printf "%.2f%%", (40/71*100) }'
```

### Factorial Function

```bash
factorial () { 
    if (($1 > 1))
    then
        echo $(( $( factorial $(($1 - 1)) ) * $1 ))
    else
        echo 1
        return
    fi
}

factorial 5  # Output: 120
```

For larger numbers, use bc:
```bash
echo 'define factorial(x) {if (x>1){return x*factorial(x-1)};return 1} factorial(50)' | bc
```

### Calculator Function

Simple calculator using bc:
```bash
calculate() { printf "%s\n" "$@" | bc -l; }
calculate "2.5 * 3.7"
```

Or using arithmetic expansion:
```bash
calculate() { echo $(("$@")); }
calculate "2 + 3"
```

### Different Number Bases

Binary (base 2):
```bash
echo $((2#1010+2#1010))  # Output: 20
```

Octal (base 8):
```bash
echo $((010+010))  # Output: 16
```

Hexadecimal (base 16):
```bash
echo $((0xA+0xA))  # Output: 20
```

### Unit Conversion Script

```bash
#!/bin/bash
echo "Enter a number to be converted:"
read number

echo "$number feet to inches:"
echo "$number*12" | bc -l

echo "$number inches to feet:"
echo "$number/12" | bc -l
```

## Common Errors and Solutions

### "value too great for base"

Occurs when using numbers outside the base range:
```bash
echo $((2#2+2#2))  # Error: 2 is not valid in binary
echo $((2#10+2#10))  # Correct: 10 in binary = 2 in decimal
```

### "syntax error: invalid arithmetic operator"

Arithmetic expansion only works with integers:
```bash
echo $((2.1+2.1))  # Error
echo "2.1+2.1" | bc -l  # Solution
```

### "integer expression expected"

The test command requires integers:
```bash
[ 1 -gt 1.5 ]  # Error
[ 1 -gt 1 ]    # Correct
```

## Best Practices

- Use arithmetic expansion `$(())` for integer calculations in scripts
- Use `bc` or `awk` for floating-point arithmetic
- Consider `printf` for formatting output
- Save frequently used calculations as functions in `.bashrc`
- Be aware of integer division limitations

---

*This document summarizes bash arithmetic operations based on information from phoenixNAP's knowledge base.*
