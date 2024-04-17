import os
import subprocess
import sys

#rename files:
# for k in range(1,3):
#     directory = rf"D:\Daten\Stefan\Revision\Frotiers Review\LGI1\Culture {k}"
#     files = os.listdir(directory)
#     for i in range(len(files)):
#         os.rename(os.path.join(directory, files[i]), os.path.join(directory, f"Culture_{k}_file{i}.tif"))
# sys.exit()

for k in range(1,7):
    directory = rf"D:\Daten\Stefan\Revision\Frotiers Review\LGI1\Culture {k}"
    channels = [[0,1],[1,2]]
    files = os.listdir(directory)
    f = []
    argument = ""
    for i in range(len(files)):

        if ".tif" in files[i]:# and files[i].split(".")[0] in HOMER_BASSON_BAD:
            f.append(files[i].split('.')[0])
            argument = files[i].split('.')[0]
            for ch in channels:
                print(subprocess.run(["python", "coloc_analysis_LGI1.py", f"directory.file_name={argument}", f"directory.culture=Culture {k}", f"params.channels={ch}"]))