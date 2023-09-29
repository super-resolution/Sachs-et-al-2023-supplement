import os
import subprocess

#todo: batch files to show


PSD_RIM= [
    "Experiment-7522-Airyscan Processing-02-5",
    "Experiment-7526-Airyscan Processing-06-4",
]

HOMER_BASSON = ["Experiment-8153-Airyscan Processing-04-2",
                "Experiment-8154-Airyscan Processing-05-2",
                "Experiment-8155-Airyscan Processing-06-12",
                "Experiment-8215-Airyscan Processing-02-2 incl synaptischer spalt"
]
HOMER_BASSON_BAD = ["Experiment-8153-Airyscan Processing-04-9",
                "Experiment-8157-Airyscan Processing-08-1",]

GLUA_MUNC = [
            "Experiment-8237-Airyscan Processing-03-3 pretty good",
            "Experiment-8237-Airyscan Processing-03-6 pretty good",
                ]

for k in range(5,7):
    directory = rf"D:\Daten\Stefan\Revision\Frotiers Review\230825_GluA1_ATTO643_LGI1_CF568_Munc13_AF488_PanExM\Culture {k}\Best"

    files = os.listdir(directory)
    f = []
    argument = ""
    for i in range(len(files)):
        if ".tif" in files[i]:# and files[i].split(".")[0] in HOMER_BASSON_BAD:
            f.append(files[i].split('.')[0])
            argument = files[i].split('.')[0]
            print(subprocess.run(["python", "create_distance_map.py", f"directory.file_name={argument}", f"directory.culture=Culture {k}"]))