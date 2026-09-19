import re
path = r"C:\Users\dpame\code\ce414-gis-applications\docs\assignments\lab-03\lab3-draft.md"
txt = open(path, encoding="utf-8").read()
section = txt.split("## Rubric for")[1]
total = 0
for line in section.splitlines():
    if not line.startswith("| **") or "Total**" in line: continue
    name = re.match(r"\| \*\*(.+?)\*\*", line).group(1)
    vals = [int(v) for v in re.findall(r"\((\d+)\)", line)]
    s = sum(vals)
    target = 5 if "up to +5" in line else 10
    print(f"{'OK ' if s==target else 'BAD'} {name[:44]:46} {vals} = {s} (want {target})")
    if "/10" in line: total += s
print(f"\nrubric rows total {total} (want 50)")
