import os
import subprocess

directory = r"D:\Daten\Stefan\Revision\Frotiers Review\230824_Homer1_ATTO643_Bassoon_CF568_CaV21_AF488_pansCF405\Culture 4\Best"

files = os.listdir(directory)
f = []
argument = ""
for i in range(len(files)):
    if ".tif" in files[i]:
        f.append(files[i].split('.')[0])
        argument +=files[i].split('.')[0]+","
argument = argument[:-1]
print(subprocess.call(["python", "calcium_evaluation.py","-m", f"directory.file_name={argument}"]))