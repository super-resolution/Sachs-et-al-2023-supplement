import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    base = "outputs_calcium"
    files = os.listdir(base)
    df = []
    n = 0

    for folder in files:
        culture = folder
        dir = os.path.join(base,folder)
        files = os.listdir(dir)
        for file in files:
            suffix = ["worst","3D"]
            post = "best"
            for s in suffix:
                if s in file:
                    post = s

            if post != "best":
                continue

            condition = "ch_[1, 2]"
            path = os.path.join(dir,file,condition)
            data = pd.read_csv(os.path.join(path, "data.txt"),sep="\t")
            data["culture"] = culture
            data["condition"] = condition
            data["subculture"] = post
            p = data["pearson"]
            transform_parameters = pd.read_csv(os.path.join(path, "tmp/affine0.txt"),sep="\t").iloc[-2].values[0]
            transform_parameters = transform_parameters.replace(")","").split(" ")
            parameters = []
            for value in transform_parameters:
                try:
                    parameters.append(float(value))
                except ValueError:
                    pass
                    #print(f"{value} is not a float")
            data["rotation"] = abs(parameters[0]/(2*np.pi)*360)
            data["translationx"] = parameters[-1]
            data["translationy"] = parameters[-2]
            data["translation"] = np.sqrt(parameters[-1]**2 +parameters[-2]**2)


            df.append(data)
            #if equal pearson throw
            n+= 1
            if p[0]<0.6:
                print(culture, file)
            # if p[0] == data["pearson"][0]:
            #     raise ValueError(f"pearsons shouldnt be equal {file}")
    df = pd.concat(df)
    df.boxplot(column="translationy", by="culture")
    plt.show()
    x=0
