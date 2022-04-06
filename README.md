# Dipolemoment-plugin
This is a plugin for PyMol 2.x to calculate and show the dipole moment vector of a proteine structure in pdb format. It is coded in Python 3 with PyQT5 (PySide2).  Charge attributions are performed using pdb2pqr (https://pdb2pqr.readthedocs.io/en/latest/getting.html) with the PARSE force field.

![image](https://user-images.githubusercontent.com/102952395/161939159-0e994963-59fd-4ad8-aae0-cb26a8b26e9c.png)

Method:\
I)   Calculate the center of Mass of the protein (COM). \
II)  Calculate a COM charge vector for each atom of the protein.\
III) Sum up all charge vectors to obtain a protein net charge Vector. \
IV)  Calculate the Dipole moment in Debye and draw the protein net charge Vector.\ 

The plugin uses numpy libraries to calculate vectors and the cgo-arrow.py script (https://github.com/gnina/scripts/blob/master/cgo_arrow.py).  
