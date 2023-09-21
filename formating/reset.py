import sys
import time
import os
output_dir = sys.argv[1]
print(f"Output directory: {output_dir}")
os.system(f"touch {output_dir}/index_register.txt")
with open(f"{output_dir}/index_register.txt", "w") as fout:
    fout.write("0\n0\n")