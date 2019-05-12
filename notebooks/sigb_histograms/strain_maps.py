from lib import strainmap
import numpy as np

strain_to_type, type_to_strain = strainmap.load()
strain_to_type = {s:t[0] for s,t in strain_to_type.items() }

cell_types = np.unique([ t for t in strain_to_type.values()])


type_to_strain = dict(zip(cell_types, [[]]*len(cell_types)))
for strain, typel in strain_to_type.items():
    type_to_strain[typel] =  type_to_strain[typel] + [strain]