import os
from xml.dom import minidom



def xml_shit(path, f_name):
    doc = minidom.parse(os.path.join(path, f_name))
    name = doc.getElementsByTagName('use')
    i = 0
    while i < len(name):
        if name[i].attributes["xlink:href"].value == "#DejaVuSans-20":
            name[i].parentNode.removeChild(name[i])
            del name[i]
        else:
            i += 1
    gs = doc.getElementsByTagName("g")
    for element in gs:
        if "id" in element.attributes.keys():
            if element.attributes["id"].value == "text_2":
                text = element
    print(text)
    text.attributes["transform"] = "translate(0.0 30.)"
    text.attributes["fill"] = "#ffffff"


    file_handle = open(f"image_to_show/"+ f_name, "w", encoding="utf-8")
    doc.writexml(file_handle)
    file_handle.close()


if __name__ == '__main__':
    HOMER_BASSOON = ""
    GlUA_MUNC = "230825_GluA1_ATTO643_LGI1_CF568_Munc13_AF488_PanExM"
    RIM_PSD = "230824_PSD95_CF568_RIM12_AF488_VGlut1_ATTO643_panExM _CF405"


    base = rf"outputs"

    files_to_use = [
                    "Experiment-7522-Airyscan Processing-02-5",
                    "Experiment-7526-Airyscan Processing-06-4",
                    ]

    bad = ["Experiment-7500-Airyscan Processing-05-3",

           ]
    files = os.listdir(base)
    df = []
    n = 0
    if not os.path.exists("image_to_show"):
        os.mkdir("image_to_show")
    for folder in files:
        if folder.split(".")[-1] == "txt":
            continue
        culture = folder
        print(culture)
        dir = os.path.join(base,folder)
        files = os.listdir(dir)
        for file in files:
            #if file in files_to_use:
                condition = "ch_[0, 2]_mix_False"
                path = os.path.join(dir, file, condition, "results")
                xml_shit(path, f"{file}False_mixup_aligned.svg")
                #delete shit
                xml_shit(path, f"{file}False_mixup_distortion.svg")
