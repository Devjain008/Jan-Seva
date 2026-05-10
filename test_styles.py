import sys
sys.path.insert(0, r'c:\Users\asus\Desktop\bfo')
from frontend.styles import get_css
css = get_css(False)
print(f"Light mode CSS length: {len(css)}")
css2 = get_css(True)
print(f"Dark mode CSS length: {len(css2)}")
print("SUCCESS: No syntax errors")
