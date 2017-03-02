from cx_Freeze import setup, Executable
import sys
import os
import subprocess
import platform
import pytz
sys.path.append('ui')
sys.path.append('images')
from libxulpymoney import version


def build_dir():
    pyversion="{}.{}".format(sys.version_info[0], sys.version_info[1])
    if sys.platform=="win32":
        so="win"
        if platform.architecture()[0]=="64bit":
            pl="amd64"
        else:
            pl="win32"
            return "build/exe.{}-{}".format(sys.platform, pyversion)
    else:#linux
        so="linux"
        if platform.architecture()[0]=="64bit":
            pl="x86_64"
        else:
            pl="i686"
    return "build/exe.{}-{}-{}".format(so, pl, pyversion)
    
def filename_output():
    if sys.platform=="win32":
        so="windows"
        if platform.architecture()[0]=="64bit":
            pl="amd64"
        else:
            pl="win32"
    else:#linux
        so="linux"
        if platform.architecture()[0]=="64bit":
            pl="x86_64"
        else:
            pl="x86"
    return "xulpymoney-{}-{}.{}".format(so,  version, pl)

def version_windows():
    lastpoint="0"
    if version.find("+")!=-1:
        lastpoint="1"
        
    versio=version.replace("+","")
    return versio[:-4]+"."+versio[4:-2]+"."+versio[6:]+"."+lastpoint

print ("Building for", sys.platform, version_windows())
name="xulpymoney"


#Add files
include_files=[ 'images/xulpymoney.ico', 'GPL-3.txt']
include_files.append(("i18n/xulpymoney_es.qm", "i18n/xulpymoney_es.qm"))
include_files.append(("i18n/xulpymoney_fr.qm", "i18n/xulpymoney_fr.qm"))
include_files.append(("i18n/xulpymoney_ro.qm", "i18n/xulpymoney_ro.qm"))
include_files.append(("i18n/xulpymoney_ru.qm", "i18n/xulpymoney_ru.qm"))
include_files.append(("sql/xulpymoney.sql", "sql/xulpymoney.sql"))

#Build options
if sys.platform=='win32':
      base = 'Win32GUI'
      include_files.append("xulpymoney.iss")
      include_files.append(pytz.__path__[0])
      build_msi_options = {
           'upgrade_code': '{3849730B-2375-4F76-B4A5-347857A23B9B}',
           'add_to_path': False,
           'initial_target_dir': r'[ProgramFilesFolder]\%s' % (name),
            }
 
      build_exe_options = dict(
            includes = ['PyQt5.QtNetwork', 'PyQt5.QtWebKit', 'PyQt5.QtPrintSupport', 'matplotlib.backends.backend_tkagg', 'tkinter', 'tkinter.filedialog', 'setuptools' ],
            excludes=[], 
            include_files=include_files)

      options={'bdist_msi': build_msi_options,
               'build_exe': build_exe_options}
else:#linux
      base="Console"
      build_options = dict(includes = [], excludes = [], include_files=include_files)
      options=dict(build_exe = build_options)

executables = [
      Executable('xulpymoney.py', base=base, icon='images/xulpymoney.ico', shortcutName= name, shortcutDir='ProgramMenuFolder'), 
      Executable('xulpymoney_init.py', base=base, icon='images/xulpymoney.ico', shortcutName= name, shortcutDir='ProgramMenuFolder')
]

setup(name=name,
      version = version_windows(),
      author = 'Mariano Muñoz',
      description = 'Finances support',
      options = options,
      executables = executables)

#Post setup
if sys.platform=="win32":
    os.chdir(build_dir())
    
    inno="c:/Program Files (x86)/Inno Setup 5/ISCC.exe"
    if platform.architecture()[0]=="32bit":
        inno=inno.replace(" (x86)", "")
    
    subprocess.call([inno,  "/o../",  "/DVERSION_NAME={}".format(version_windows()), "/DFILENAME={}".format(filename_output()),"xulpymoney.iss"], stdout=sys.stdout)
else:   #Linux
    print (build_dir(), filename_output(), os.getcwd())
    pwd=os.getcwd()
    os.chdir(build_dir())
    print (build_dir(), filename_output(), os.getcwd())
    os.system("tar cvz -f '{0}/build/{1}.tar.gz' * -C '{0}/{2}/'".format(pwd, filename_output(),  build_dir()))

