import pickle


data_pickle = {"name": ["Clay", "Sand", "Rock"],
               "properties": {"Clay": [30, .3, 2, 10, 30],
                              "Sand": [20, .3, 1.9, 10, 30],
                              "Rock": [80, .3, 2.1, 10, 30]
                              },
               }


with open("materials.pickle", 'wb') as f:
    pickle.dump(data_pickle, f)

with open("materials.pickle", 'rb') as f:
    load_data = pickle.load(f)
print(load_data)
