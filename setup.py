from setuptools import setup, Command

import gettext
import logging
import os
import platform
import site
import sys
from PyQt5.QtCore import QCoreApplication,  QTranslator
from colorama import Style, Fore
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

def change_language(language):  
    """language es un string"""
    url= "xulpymoney/qm/xulpymoney_{}.qm".format(language)
    if os.path.exists(url)==True:
        translator.load(url)
        QCoreApplication.installTranslator(translator)
        logging.info(("Language changed to {} using {}".format(language, url)))
        return
    if language!="en":
        logging.warning(Style.BRIGHT+ Fore.CYAN+ app.tr("Language ({}) couldn't be loaded in {}. Using default (en).".format(language, url)))

class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
#        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
#        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/xulpymoney/ --delete-after")
        os.chdir("..")

class Compile(Command):
    description = "Compile ui and images"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        futures=[]
        with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
            for filename in os.listdir("xulpymoney/ui/"):
                if filename.endswith(".ui"):
                    without_extension=filename[:-3]
                    futures.append(executor.submit(os.system, "pyuic5 xulpymoney/ui/{0}.ui -o xulpymoney/ui/Ui_{0}.py".format(without_extension)))
            futures.append(executor.submit(os.system, "pyrcc5 xulpymoney/images/xulpymoney.qrc -o xulpymoney/images/xulpymoney_rc.py"))
        # Overwriting xulpymoney_rc
        for filename in os.listdir("xulpymoney/ui/"):
             if filename.startswith("Ui_"):
                 os.system("sed -i -e 's/xulpymoney_rc/xulpymoney.images.xulpymoney_rc/' xulpymoney/ui/{}".format(filename))
        # Overwriting myQGLWidget
#        os.system("sed -i -e 's/from myQGLWidget/from xulpymoney.ui.myQGLWidget/' xulpymoney/ui/Ui_wdgGame.py")
#        os.system("sed -i -e 's/from myQGLWidget/from xulpymoney.ui.myQGLWidget/' xulpymoney/ui/Ui_frmAbout.py")
        # Overwriting qtablestatistics
#        os.system("sed -i -e 's/from qtablestatistics/from xulpymoney.ui.qtablestatistics/' xulpymoney/ui/Ui_wdgGame.py")


class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform.system()=="Linux":
            os.system("rm -Rf {}/xulpymoney*".format(site.getsitepackages()[0]))
            os.system("rm /usr/bin/xulpymoney*")
            os.system("rm /usr/share/pixmaps/xulpymoney.png")
            os.system("rm /usr/share/applications/xulpymoney.desktop")
        else:
            print(_("Uninstall command only works in Linux"))

class Doc(Command):
    description = "Update man pages and translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("pylupdate5 -noobsolete -verbose xulpymoney.pro")
        os.system("lrelease -qt5 xulpymoney.pro")
    ########################################################################

app=QCoreApplication(sys.argv)

app.setOrganizationName("xulpymoney")
app.setOrganizationDomain("xulpymoney.sourceforge.net")
app.setApplicationName("xulpymoney")
translator=QTranslator()
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

if platform.system()=="Linux":
    data_files=[]
    #('/usr/share/man/man1/', ['man/man1/xulpymoney.1']), 
    #            ('/usr/share/man/es/man1/', ['man/es/man1/xulpymoney.1'])
    #           ]
else:
    data_files=[]

## Version of officegenerator captured from commons to avoid problems with package dependencies
__version__= None
with open('xulpymoney/version.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]

setup(name='xulpymoney',
    version=__version__,
    description='Parchís game',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'Topic :: Software Development :: Build Tools',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Programming Language :: Python :: 3',
             ], 
    keywords='parchís game',
    url='https://xulpymoney.sourceforge.io/',
    author='Turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['xulpymoney'],
    entry_points = {'console_scripts': [    'xulpymoney=xulpymoney.xulpymoney:main',
                                    ],
                },
    install_requires=['PyQt5', 'pyopengl','setuptools'],
    data_files=data_files,
    cmdclass={
                        'doxygen': Doxygen,
                        'doc': Doc,
                        'uninstall':Uninstall, 
                        'compile': Compile, 
                     },
    zip_safe=False,
    include_package_data=True
    )

_=gettext.gettext#To avoid warnings
