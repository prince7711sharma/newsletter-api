with open("app/dashboard_template.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the start and end of the f-string
start = content.find('f"""') + 4
end = content.rfind('"""')

f_string_content = content[start:end]

open_braces = 0
close_braces = 0

for i, char in enumerate(f_string_content):
    if char == '{':
        open_braces += 1
    elif char == '}':
        close_braces += 1

print(f"Open: {open_braces}, Close: {close_braces}")

# Find un-doubled braces
i = 0
while i < len(f_string_content):
    if f_string_content[i] == '{':
        if i + 1 < len(f_string_content) and f_string_content[i+1] == '{':
            i += 2
        else:
            # Check if it's the valid {admin_key}
            if f_string_content[i:i+11] == '{admin_key}':
                i += 11
            else:
                print(f"Single '{{' at index {i}: {f_string_content[i:i+20]}")
                i += 1
    elif f_string_content[i] == '}':
        if i + 1 < len(f_string_content) and f_string_content[i+1] == '}':
            i += 2
        else:
            # Check if it's the valid {admin_key}
            # We already handled { start, so this } might be the closing one
            # But our loop is simple. Let's just flag all single }
            print(f"Single '}}' at index {i}: {f_string_content[i-10:i+1]}")
            i += 1
    else:
        i += 1
