# python bitwise_ops.py > ..\src\mcbuild\test\test.mcb

import random


def to_int32(n):
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n > 0x7FFFFFFF else n


def gen_tests():
    # Define operations with exact argument counts and corresponding logic
    # Format: (name, arg_count, lambda_function)
    ops = [
        # Binary Ops (2 inputs + 1 output = 3 args passed to template, but logic takes 2 inputs)
        ("and", 3, lambda a, b: to_int32(a & b)),
        ("or", 3, lambda a, b: to_int32(a | b)),
        ("xor", 3, lambda a, b: to_int32(a ^ b)),
        # Unary Op (1 input = 1 arg passed to template, logic takes 1 input)
        ("not", 1, lambda a: to_int32(~a)),
        # Comparison Ops (2 inputs + 1 output = 3 args passed, logic takes 2 inputs)
        (
            "bigger_than_unsigned",
            3,
            lambda a, b: 1 if (a & 0xFFFFFFFF) > (b & 0xFFFFFFFF) else 0,
        ),
        (
            "bigger_than_or_equal_unsigned",
            3,
            lambda a, b: 1 if (a & 0xFFFFFFFF) >= (b & 0xFFFFFFFF) else 0,
        ),
        # Shift Left (2 args total in template: input_a, input_b. Modifies input_a)
        # Your template: with input_a:word input_b:word
        ("shift_left_logical", 2, lambda a, b: to_int32(a << (b & 0x1F))),
        # Shift Right Logical (3 args total: input_a, input_b, output)
        (
            "shift_right_logical",
            3,
            lambda a, b: to_int32((a & 0xFFFFFFFF) >> (b & 0x1F)),
        ),
        # Shift Right Arithmetic (3 args total: input_a, input_b, output)
        ("shift_right_arithmetic", 3, lambda a, b: to_int32(a >> (b & 0x1F))),
    ]

    for name, argc, func in ops:
        print(f"\t# Testing {name}")
        for i in range(1000):
            # Generate random 32-bit signed integers based EXACTLY on argc
            args = [random.randint(-2147483648, 2147483647) for _ in range(argc)]

            # Special handling for shift amounts to keep them sane (0-31)
            if "shift" in name:
                # The second argument is always the shift amount in our definition
                args[1] = random.randint(0, 31)

            # Calculate expected result
            # Unpack exactly what the lambda expects
            if argc == 1:
                expected = func(args[0])
            elif argc == 2:
                expected = func(args[0], args[1])
            elif argc == 3:
                expected = func(args[0], args[1])
            else:
                raise ValueError(f"Unsupported arg count {argc}")

            # --- Generate MC Commands ---

            # Set Inputs
            print(f"\tscoreboard players set #1 test {args[0]}")
            if argc >= 2:
                print(f"\tscoreboard players set #2 test {args[1]}")

            # Initialize Output if needed (for 3-arg templates where #3 is output)
            if argc == 3:
                print(f"\tscoreboard players set #3 test 0")

            # Build Template Call String
            call_args = " ".join([f"#{j+1}@test" for j in range(argc)])
            print(f"\ttemplate {name} {call_args}")

            # Determine Result Scoreboard
            # 'not' and 'shift_left_logical' modify #1 directly
            # Others write to #3
            result_slot = 1 if name in ["not", "shift_left_logical"] else 3

            # Verification Command
            print(
                f"\texecute unless score #{result_slot} test matches {expected} run say FAIL:{name}:in({args})_exp({expected})"
            )


if __name__ == "__main__":
    print("import ./org_jawbts_riscvmc2_bitwise_ops_t.mcbt\nfunction test {")
    gen_tests()
    print("\tsay Finshed.")
    print("}")
