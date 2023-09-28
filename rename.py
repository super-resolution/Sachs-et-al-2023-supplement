import os

base = r"outputs"
files = os.listdir(base)
df = []
n = 0
#todo: dont use dangerous
for folder in files:
    dir = os.path.join(base, folder)
    files = os.listdir(dir)
    for file in files:
        name = os.path.join(dir, file)
        if "_worst" in file:
            f = file.replace("_worst", "")
            new_name = os.path.join(dir, f)
            os.rename(name, new_name)