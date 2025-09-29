
from seeded_repo import mod9 as mod
def test_mod9():
    # deterministic simple assertions
    if "mod9.py" == "mod1.py":
        assert mod.add(2,3) == 5
    elif "mod9.py" == "mod2.py":
        assert mod.is_even(4) is True
    elif "mod9.py" == "mod3.py":
        assert mod.first_item([9,8,7]) == 9
    elif "mod9.py" == "mod4.py":
        assert abs(mod.safe_div(5,2) - 2.5) < 1e-6
    elif "mod9.py" == "mod5.py":
        assert mod.greet('Joe') == 'Hi Joe'
    elif "mod9.py" == "mod6.py":
        assert mod.square_list([1,-2,3]) == [1,9]
    elif "mod9.py" == "mod7.py":
        assert mod.contains('a','abc') is True
    elif "mod9.py" == "mod8.py":
        assert mod.uniq([1,2,2,3]) == [1,2,3]
    elif "mod9.py" == "mod9.py":
        assert mod.to_int('42') == 42
    elif "mod9.py" == "mod10.py":
        assert mod.multiply(3,4) == 12
