import re

# This regex checks imports only
REGEX = r"""^(import|from)\s+(\w+\.)*\w+
(\s+as\s+\w+)?\s+(import\s+(\w+\.)*\w+
(\s+as\s+\w+)?(\s*,\s*(\w+\.)*\w+(\s+as\s+\w+)?)*)?$"""

INPUT_STR = """import os
import sys as s
from abc import ABC, abstractmethod
from typing import List, Tuple
from math import pi, sqrt
import numpy as np
import pandas as pd, matplotlib.pyplot as plt
"""

if re.match(REGEX, INPUT_STR, re.MULTILINE):
    print("Valid imports detected.")
else:
    print("Invalid imports detected.")
