# Code-quality-auditor
import os

def analyze_code(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    total_lines = len(lines)
    comment_lines = len([l for l in lines if '#' in l])
    blank_lines = len([l for l in lines if l.strip() == ""])
    function_count = len([l for l in lines if l.strip().startswith("def ")])

    print(f"📄 File: {filename}")
    print(f"🔢 Total lines: {total_lines}")
    print(f"💬 Comment lines: {comment_lines}")
    print(f"⬜ Blank lines: {blank_lines}")
    print(f"🧠 Functions: {function_count}")
    print("-" * 40)

# Example usage
analyze_code("test.py")

