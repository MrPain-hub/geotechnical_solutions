import pickle

data = {"materials": ["Clay", "Sand", "Gravel", "Silt", "Rock"]}
with open("materials.pickle", 'wb') as f:
    pickle.dump(data, f)
    #data = pickle.load(f)

with open("materials.pickle", 'rb') as f:
    data1 = pickle.load(f)

print(data1.get('materials'))

