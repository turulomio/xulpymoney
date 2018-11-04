from cx_Freeze import setup, Executable
import sys
import pytz
sys.path.append('ui')
sys.path.append('images')
from libxulpymoneyversion import version_windows,  version

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
    finalversion=version_windows()
    base = 'Win32GUI'
    include_files.append("xulpymoney.iss")
    include_files.append(pytz.__path__[0])
    build_msi_options = {
           'upgrade_code': '{3849730B-2375-4F76-B4A5-347857A23B9B}',
           'add_to_path': False,
           'initial_target_dir': r'[ProgramFilesFolder]\%s' % (name),
            }
 
    build_exe_options = dict(
        includes = ['PyQt5.QtNetwork',  'PyQt5.QtPrintSupport', 'setuptools',],#'numpy.core._methods','numpy.lib.format' ],
        excludes=[], 
        include_files=include_files)

    options={'bdist_msi': build_msi_options,
             'build_exe': build_exe_options}
else:#linux
    base="Console"
    finalversion=version
    build_options = dict(includes = [], excludes = [], include_files=include_files)
    options={'build_exe' : build_options}

executables = [
    Executable('xulpymoney.py', base=base, icon='images/xulpymoney.ico', shortcutName= name, shortcutDir='ProgramMenuFolder'), 
    Executable('xulpymoney_init.py', base=base, icon='images/xulpymoney.ico', shortcutName= name, shortcutDir='ProgramMenuFolder')
]

setup(name=name,
    version = finalversion,
    author = 'Mariano Muñoz',
    author_email="turulomio@yahoo.es", 
    description = 'Personal and finances accounting system',
    options = options,
    url="https://sourceforge.net/projects/xulpymoney/", 
    executables = executables)

