import json
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import os
import hptlc
import config

def mesure_distances(main_folder_path, name):

    # Open sample of interest
    with open(f"{main_folder_path}/standard/{name}.json", 'r') as openfile:
        main_object = json.load(openfile)


    columns_to_compare = []
    main_to_compare = []

    for elu in main_object:
        for obs in main_object[elu]:
            if main_object[elu][obs]['R'] != []:
                columns_to_compare.append((elu, obs))

                main_data = main_object[elu][obs]
                main_to_compare.append(np.array([main_data['R'],
                                                main_data['G'],
                                                main_data['B']]))

    if columns_to_compare == []:
        print(f"{name}.json is empty. Nothing to compare with.")

    else:
        others = [f for f in listdir(main_folder_path+"/standard/") if isfile(join(main_folder_path+"/standard/", f))]
        others.remove(name+".json")

        all_distances = []
        for other in others:
            with open(f"{main_folder_path}/standard/{other}", 'r') as openfile:
                other_object = json.load(openfile)


            distances = []
            for idx, columns in enumerate(columns_to_compare):
                other_data = other_object[columns[0]][columns[1]]
                if other_data['R'] != []:
                    other_to_compare = np.array([other_data['R'],
                                                    other_data['G'],
                                                    other_data['B']])

                    distances.append(compute_single_distance(main_to_compare[idx], other_to_compare))

            if distances != []:
                all_distances.append(np.mean(distances))

            else:
                all_distances.append(np.nan)
        
        new_others = [k[:-5] for k in others if k[-5:]=='.json']

        if not os.path.isdir(main_folder_path + "distances"):
            os.makedirs(main_folder_path + "distances")

        to_dump = pd.DataFrame(data={"Name":new_others, "Distance":all_distances})
        to_dump = to_dump.dropna(ignore_index=True)
        to_dump = to_dump.sort_values("Distance")
        to_dump.to_csv(main_folder_path + 'distances/' + name + ".csv", index=False)
        

def compute_single_distance(data1, data2):
    diff = abs(data1 - data2)
    distance = np.sum(diff)/np.shape(data1)[1]
    return 100*distance

def show_results(main_folder_path, name, n=5):

    #In case the user inputs a file
    if name[-4:]=='.csv':
        name = name[:-4]

    df = pd.read_csv(f"{main_folder_path}/distances/{name}.csv")

    ord_dist, ord_others = df['Distance'], df['Name']

    print(f"\nSamples most similar to {name}:\n")
    for i in range(min(n, len(ord_others))):
        print(f"{ord_others[i]} : {ord_dist[i]:.1f}")

    print('___________________\n')


def main():
    
    main_folder_path = hptlc.HPTLC_extracter.main_folder_path

    for name in config.compute_distances:
        mesure_distances(main_folder_path, name)
        show_results(main_folder_path, name, n=config.show_n_best)

        