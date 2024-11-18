# test_imports.py
import sys
print("Python version:", sys.version)
print("Python path:", sys.path)
print("Attempting to import required packages...")

try:
    import requests
    print("✓ requests imported successfully")
except ImportError as e:
    print("✗ Failed to import requests:", e)

try:
    import pandas
    print("✓ pandas imported successfully")
except ImportError as e:
    print("✗ Failed to import pandas:", e)

try:
    import httpx
    print("✓ httpx imported successfully")
except ImportError as e:
    print("✗ Failed to import httpx:", e)

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
except ImportError as e:
    print("✗ Failed to import python-dotenv:", e)
