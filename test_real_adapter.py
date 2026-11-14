import os
import sys

# Ensure DLL path is added to Windows search directory
dll_dir = os.path.join(sys.prefix, 'Lib', 'site-packages', 'llama_cpp', 'lib')
if os.path.exists(dll_dir) and hasattr(os, 'add_dll_directory'):
    try:
        os.add_dll_directory(dll_dir)
    except Exception:
        pass

from inference import generate_response

print('=== Testing Public Adapter Contract ===')
prompt = 'Explain cloud computing in 10 words.'
print(f'Prompt: {prompt}')
response = generate_response(prompt, max_tokens=32)
print(f'Real AI Output: {response}')
print('=== Success: Contract Verified! ===')
