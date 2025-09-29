# create_seeded_repo.py
import os, textwrap

os.makedirs("seeded_repo", exist_ok=True)
os.makedirs("tests", exist_ok=True)
os.makedirs("gold_fixes", exist_ok=True)

files = {
    "mod1.py": ("def add(a,b):\n    return a - b\n", "def add(a,b):\n    return a + b\n"),
    "mod2.py": ("def is_even(n):\n    return n % 2 == 1\n", "def is_even(n):\n    return n % 2 == 0\n"),
    "mod3.py": ("def first_item(lst):\n    return lst[1]\n", "def first_item(lst):\n    return lst[0]\n"),
    "mod4.py": ("def safe_div(a,b):\n    return a // b\n", "def safe_div(a,b):\n    return a / b\n"),
    "mod5.py": ("def greet(name):\n    return 'Hi' + name\n", "def greet(name):\n    return 'Hi ' + name\n"),
    "mod6.py": ("def square_list(xs):\n    return [x*x for x in xs if x>0]\n", "def square_list(xs):\n    return [x*x for x in xs]\n"),
    "mod7.py": ("def contains(sub,s):\n    return s.find(sub) > 0\n", "def contains(sub,s):\n    return s.find(sub) >= 0\n"),
    "mod8.py": ("def uniq(xs):\n    return list(xs)\n", "def uniq(xs):\n    return list(dict.fromkeys(xs))\n"),
    "mod9.py": ("def to_int(s):\n    return int(float(s))\n", "def to_int(s):\n    return int(s)\n"),
    "mod10.py": ("def multiply(a,b=2):\n    return a + b\n", "def multiply(a,b=2):\n    return a * b\n"),
}

for i,(fname,(bug,fix)) in enumerate(files.items(),1):
    with open(f"seeded_repo/{fname}","w") as f:
        f.write(bug)
    with open(f"gold_fixes/{fname}","w") as f:
        f.write(fix)
    test_name = f"tests/test_{fname.replace('.py','')}.py"
    test_code = textwrap.dedent(f"""
    from seeded_repo import {fname.replace('.py','')} as mod
    def test_{fname.replace('.py','')}():
        # deterministic simple assertions
        if "{fname}" == "mod1.py":
            assert mod.add(2,3) == 5
        elif "{fname}" == "mod2.py":
            assert mod.is_even(4) is True
        elif "{fname}" == "mod3.py":
            assert mod.first_item([9,8,7]) == 9
        elif "{fname}" == "mod4.py":
            assert abs(mod.safe_div(5,2) - 2.5) < 1e-6
        elif "{fname}" == "mod5.py":
            assert mod.greet('Joe') == 'Hi Joe'
        elif "{fname}" == "mod6.py":
            assert mod.square_list([1,-2,3]) == [1,9]
        elif "{fname}" == "mod7.py":
            assert mod.contains('a','abc') is True
        elif "{fname}" == "mod8.py":
            assert mod.uniq([1,2,2,3]) == [1,2,3]
        elif "{fname}" == "mod9.py":
            assert mod.to_int('42') == 42
        elif "{fname}" == "mod10.py":
            assert mod.multiply(3,4) == 12
    """)
    with open(test_name,"w") as f:
        f.write(test_code)
        
# create __init__.py for the seeded_repo package
with open("seeded_repo/__init__.py","w") as f:
    f.write("")
    
print("seeded repo created: seeded_repo/, tests/, gold_fixes/")