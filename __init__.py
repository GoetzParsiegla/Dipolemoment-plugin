# This Python 3.x file uses the following encoding: utf-8
# dipolemaker plugin for PyMol 2.x (Windows version) Copyright Notice.
# ====================================================================
#
# The dipolemaker plugin source code is copyrighted, but you can freely
# use and copy it as long as you don't change or remove any of the
# copyright notices.
#
# ----------------------------------------------------------------------
# Dipolemaker plugin is Copyright (C) 2020 by Goetz Parsiegla
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of Goetz Parsiegla not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# GOETZ PARSIEGLA DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS.  IN NO EVENT SHALL DANIEL SEELIGER BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------
#
# It calculates and shows the dipolemoment of a proteine as an arrow 
# If you find bugs or have any suggestions for future versions contact me:
# goetz.parsiegla@imm.cnrs.fr

import sys
import os
import numpy as np
from pymol import cmd

def __init_plugin__(app=None):
    '''
    Add an entry to the PyMOL "Plugin" menu
    '''
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Dipolemaker', run_plugin_gui)


# global reference to avoid garbage collection of our dialog
dialog = None

def run_plugin_gui():
    # pymol.Qt is a wrapper which provides the PySide2/Qt5/Qt4 interface
    # if it has been installed in python before
    from pymol.Qt import QtWidgets

    global dialog
    if dialog is None:
        dialog = QtWidgets.QDialog() # now global dialog holds an object

    # filename of our UI file
    uifile = os.path.join(os.path.dirname(__file__), 'form.ui')

    # load the UI file into our dialog
    from pymol.Qt.utils import loadUi
    form = loadUi(uifile, dialog)

    # ----------- Plugin code starts here ----------------

    # get a temporary file directory
    if not sys.platform.startswith('win'):
        home = os.environ.get('HOME')
    else:
        home = os.environ.get('HOMEPATH')

    tmp_dir = os.path.join(home, '.PyMol_plugin')
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
        print("Created temporary files directory:  %s" % tmp_dir)

    # Assign nonlocal variables to lineEdits and spinBoxes  
    pdb2pqr_data_location = form.lineEdit
    cgoarrow_script_location = form.lineEdit_2
    statusline = form.lineEdit_3
    set_pH = form.doubleSpinBox_2
    set_pH.setSingleStep(1.0)
    set_vectorscale = form.doubleSpinBox
    set_vectorscale.setSingleStep(0.1)

    #---------------------------------------------------------------------------------------
    #  nonlocal defaults             
    config_settings = {}
    selected_prot = ""
    pdb2pqr_data_path = ""
    cgoarrow_script_path = ""
    pdb2pqr_forcefield = "parse"
    pH_value = 7.00
    vector_scale = 0.30
    #---------------------------------------------------------------------------------------

    # Config page

    install_text = """<html><body>This version of the Dipolemaker Plugin is planned to be used
    under Windows.<br>To run Dipolemaker, you have to install pdb2pqr (version 2.1.1 from
    sourceforge.net).<br>You also need the cgo_arrow.py script ((c) 2013 Thomas Holder,
    Schrodinger Inc.) which can be downloaded from the PyMOLWiki.</body></html>
    """

    def set_statusline(text):
        statusline.clear()
        statusline.insert(text)

    # Config functions
        
    def get_pdb2pqr_path():
        dirdialog = QtWidgets.QFileDialog()
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        if dirdialog.exec_():
            dirname = ''.join(
                map(str, dirdialog.selectedFiles()))+'/'
            set_pdb2pqr_data_path(dirname)
        else:
            None

    def get_cgoarrow_script_path():
        dirdialog = QtWidgets.QFileDialog()
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        if dirdialog.exec_():
            dirname = ''.join(
                map(str, dirdialog.selectedFiles()))+'/'
            set_cgoarrow_script_path(dirname)
        else:
            None

    def set_pdb2pqr_data_path(dirname):
        nonlocal pdb2pqr_data_path
        pdb2pqr_data_location.clear()
        pdb2pqr_data_location.insert(dirname)
        pdb2pqr_data_path = dirname
        config_settings['pdb2pqr_data_path'] = dirname

    def set_cgoarrow_script_path(dirname):
        nonlocal cgoarrow_script_path
        cgoarrow_script_location.clear()
        cgoarrow_script_location.insert(dirname)
        cgoarrow_script_path = dirname
        config_settings['cgoarrow_script_path'] = dirname

    def work_dir():
        return os.path.abspath(os.curdir)

    def read_plugin_config_file():
        config_file_name = os.path.join(tmp_dir, "dipolemaker2_plugin.conf")
        config_settings = {}
        config_settings['pdb2pqr_data_path'] = ''
        config_settings['cgoarrow_script_path'] = ''
        if os.path.isfile(config_file_name):
            set_statusline('Reading configuration file: %s' % config_file_name)
            lst = fileopen(config_file_name, 'r').readlines()
            for line in lst:
                if line[0] != '#':
                    entr = line.split('=')
                    config_settings[entr[0].strip()] = entr[1].strip()
            set_pdb2pqr_data_path(
                config_settings['pdb2pqr_data_path'])
            set_cgoarrow_script_path(
                config_settings['cgoarrow_script_path'])
        else:
            set_statusline('Configuration file not found')
        return config_settings

    def save_plugin_config_file():
        config_file_name = os.path.join(tmp_dir, "dipolemaker2_plugin.conf")
        fp = fileopen(config_file_name, 'w')
        print('#========================================', file=fp)
        print('# Dipolemaker Plugin configuration file', file=fp)
        config_settings['pdb2pqr_data_path'] = pdb2pqr_data_location.text()
        config_settings['cgoarrow_script_path'] = cgoarrow_script_location.text()
        for key, val in config_settings.items():
            print(key, '=', val, file=fp)
        fp.close()
        set_statusline('Wrote configuration file %s' % config_file_name)

    def fileopen(filename, mode):
        if mode == 'w' and os.path.isfile(filename):
            p = os.path.abspath(filename)
            b = os.path.basename(p)
            pa, n = p.split(b)
            tmp = '#'+b+'#'
            fn = os.path.join(pa, tmp)
            if os.path.exists(fn):
                os.remove(fn)
                os.rename(filename, fn)
            else:
                os.rename(filename, fn)
            set_statusline('Backing up %s to %s' % (filename, fn))
        try:
            fp = open(filename, mode)
            return fp
        except:
            set_statusline('Error','Could not open file %s' % filename)
            return None

    # Run page buildup
    form.textBrowser.setHtml(install_text)
    config_settings = read_plugin_config_file()

    #------------------------------------------------------------------

    # Dipolemaker page

    # popka_mode settings
    form.checkBox.setChecked(False)

    # pdb2pqr forcefields
    allforcefields = ['amber','charmm','parse','tyl06','peopb','swanson']

    intro_text = """<html><body>
    Calculates the dipole moment of a structure and creates a dipole vector cgo object<br>
    Uses pdb2pqr to attribute charges, may use propka to calculate them at a specific pH<br> 
    1. Open the structure in PyMol<br>
    2. Import and select it in the plugin<br>
    3. Run pdb2pqr to add charges<br>
    4. Calculate the Dipole
    </body></html>"""

    # Dipole object selection functions

    def import_objects():
        form.comboBox.clear()
        lst = cmd.get_names("selections")+cmd.get_names()
        if 'sele' in lst:
            lst.remove('sele')
        if 'cgo' in lst:
            lst.remove('cgo')
        lst.insert(0, '')
        object_list = lst
        form.comboBox.addItems(object_list)

    # pdb2pqr functions

    def run_pdb2pqr():
        nonlocal selected_prot
        selected_prot = form.comboBox.currentText()
        if selected_prot == "":
            set_statusline("No structure selected")
        else:
            cmd.center(selected_prot)
            cmd.save("temp.pdb",selected_prot)
            pdb2pqr_forcefield = form.comboBox_2.currentText()
            if form.checkBox.isChecked() == True: 
                pH_value = set_pH.value()
                pdb2pqr_exe = '"'+(os.path.join(pdb2pqr_data_path,"pdb2pqr.exe"))+'"'
                outfilename = '"'+(os.path.join(work_dir(),"%s.pqr" % selected_prot))+'"'
                command = 'call %s --ff=%s --drop-water --ph-calc-method=propka --with-ph=%s temp.pdb %s' % (pdb2pqr_exe,pdb2pqr_forcefield,pH_value,outfilename)
                print(command)
                os.system(command)
            else:
                pdb2pqr_exe = '"'+(os.path.join(pdb2pqr_data_path,"pdb2pqr.exe"))+'"'
                outfilename = '"'+(os.path.join(work_dir(),"%s.pqr" % selected_prot))+'"'
                command = 'call %s --ff=%s --drop-water temp.pdb %s' % (pdb2pqr_exe,pdb2pqr_forcefield,outfilename)
                print(command)
                os.system(command)
            if os.path.isfile(selected_prot+".pqr"):
                os.remove("temp.pdb")
            cmd.delete(selected_prot)
            cmd.load(selected_prot+".pqr")
            set_statusline("Created and loaded %s.pqr" % selected_prot)

    # Calculate dipole vector

    def makedipole_object_selected():
        if selected_prot == "":
            set_statusline("No structure selected")
        else:
            showVector = True  # change to "False" to hide dipole vector
            vectorScale = set_vectorscale.value()  # may want to increase/decrease for better presentation
            cgoarrow_script = (os.path.join(cgoarrow_script_path,"cgo_arrow.py"))
            
            # this is a variant of the chimera script for dipole calculation
            # it needs at least pymol version 1.7.2 , numpy and the cgo_arrow.py script to work correctly 
            # you also need to have a file with partial charges loaded (.pqr or .mol2)

            # calculation method conscripted from:
            #	A server and database for dipole moments of proteins
            #	Nucleic Acids Res. 2007 Jul;35(Web Server issue):W512-21
            #	doi:10.1093/nar/gkm307


            atoms = cmd.get_model(selected_prot)
            com = np.array(cmd.centerofmass(selected_prot))
            print("Center of mass: ", com)
            dipole = np.zeros(3) # set dipole vector to 0 at start 
            for at in atoms.atom:
                    coor = np.array(at.coord)
            #        print "adding atom charge : ", at.resn, at.resi, at.name, coor, at.partial_charge
                    try:
                            dipole += at.partial_charge * (coor - com)
                    except AttributeError:
                            raise UserError("No charge assigned to %s" % at.name)
            # 4.803 is conversion factor to Debyes for angstrom measurements
            set_statusline("Dipole moment for %s : %.3f Debeye" % (selected_prot, np.linalg.norm(4.803 * dipole)))
            if showVector:
                    cgoname="dipole-"+selected_prot
                    cmd.delete(cgoname) # replace ancient cgo if present
                    v = com + (vectorScale * dipole)
                    if dipole.any()<0:
                            orient= "blue red"
                    else:
                            orient ="red blue"
                    if not os.path.isfile(cgoarrow_script):
                            print("Could not find cgo_arrow.py in %s" % (cgoarrow_script_path)) 
                    else:
                            cmd.do ("run "+cgoarrow_script)
                            cmd.do ("cgo_arrow [%s, %s, %s],[%s, %s, %s],gap=1.0,color=%s,name=%s" % (com[0],com[1],com[2],v[0],v[1],v[2],orient,cgoname))
                            cmd.enable(cgoname)

    # launch on startup :
    import_objects()

    # Run page buildup
    form.textBrowser_2.setHtml(intro_text)
    form.comboBox_2.addItems(allforcefields)
    form.comboBox_2.setCurrentText(pdb2pqr_forcefield)        
    form.comboBox.setCurrentText(selected_prot)
    form.doubleSpinBox_2.setValue(pH_value)
    form.doubleSpinBox.setValue(vector_scale)

    #------------------------------------------------------------------

    # ---------------------------------------------
    # All Button bindings :

    form.pushButton.clicked.connect(import_objects)
    form.pushButton_1.clicked.connect(get_pdb2pqr_path)
    form.pushButton_2.clicked.connect(get_cgoarrow_script_path)
    form.pushButton_3.clicked.connect(save_plugin_config_file)
    form.pushButton_4.clicked.connect(run_pdb2pqr)
    form.pushButton_5.clicked.connect(makedipole_object_selected)
    # ----------------------------------------------


    # --- Plugin code ends here, now show the global dialog object ---

    dialog.show()





