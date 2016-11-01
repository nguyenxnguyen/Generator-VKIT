import re

x = """
DISCOVER MODE: x
Application
LanWan
RouterSwitch

ENVIRONMENT VARIABLE:
NH_DISCOVER_SNMPV2C_ONLY = Yes
"""
b = "DISCOVER MODE"
a = b + ".*\n{2,}"
pattern = re.compile(a, re.DOTALL)
y = re.search(pattern, x)
count_y = len(y.group())
print count_y