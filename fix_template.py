import os

file_path = "app/dashboard_template.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove f prefix
content = content.replace('return f"""', 'html = """')

# 2. Fix the end
content = content.replace('</html>"""', '</html>""".replace("{admin_key}", admin_key)\n    return html')

# 3. Replace all {{ and }} with { and }
# We must be careful not to break the replace() part we just added
# So we'll do it only on the string part.
start_idx = content.find('html = """') + 10
end_idx = content.rfind('</html>"""') + 7
string_part = content[start_idx:end_idx]

string_part = string_part.replace('{{', '{').replace('}}', '}')

new_content = content[:start_idx] + string_part + content[end_idx:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)
