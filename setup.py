from setuptools import setup, Command
import os
import platform
import shutil
import site
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.system("rm -Rf build")
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/xulpymoney/ --delete-after")
        os.chdir("..")
class PyInstaller(Command):
    description = "We run pyinstaller in build to avoid doing a ./xulpymoney module imort. I had problems with i18n. Before running this command I must have done a install, removing old installations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("python setup.py uninstall")
        os.system("python setup.py install")
        f=open("build/run.py","w")
        f.write("import xulpymoney\n")
        f.write("xulpymoney.main()\n")
        f.close()
        os.chdir("build")
        os.system("""pyinstaller run.py -n xulpymoney-{} --onefile --windowed --icon ../xulpymoney/images/xulpymoney.ico --distpath ../dist""".format(__version__))

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
                 os.system("sed -i -e 's/from canvaschart/from xulpymoney.ui.canvaschart/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from myqlineedit/from xulpymoney.ui.myqlineedit/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from myqtablewidget/from xulpymoney.ui.myqtablewidget/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from xulpymoney.ui.myqlineedit/from xulpymoney.ui.myqlineedit/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from wdgTwoCurrencyLineEdit/from xulpymoney.ui.wdgTwoCurrencyLineEdit/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from wdgCurrencyConversion/from xulpymoney.ui.wdgCurrencyConversion/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from wdgProductSelector/from xulpymoney.ui.wdgProductSelector/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from wdgDatetime/from xulpymoney.ui.wdgDatetime/' xulpymoney/ui/{}".format(filename))
                 os.system("sed -i -e 's/from wdgYear/from xulpymoney.ui.wdgYear/' xulpymoney/ui/{}".format(filename))

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
            os.system("rm /usr/bin/xulpymone*")
            os.system("rm /usr/share/pixmaps/xulpymoney.png")
            os.system("rm /usr/share/applications/xulpymoney.desktop")
        else:
            print(site.getsitepackages())
            for file in os.listdir(site.getsitepackages()[1]):#site packages
                path=site.getsitepackages()[1]+"\\"+ file
                if file.find("xulpymoney")!=-1:
                    shutil.rmtree(path)
                    print(path,  "Erased")
            for file in os.listdir(site.getsitepackages()[0]+"\\Scripts\\"):#Scripts
                path=site.getsitepackages()[0]+"\\scripts\\"+ file
                if file.find("xulpymoney")!=-1:
                    os.remove(path)
                    print(path,  "Erased")

class Procedure(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("""
Nueva versión:
  * Cambiar la versión y la fecha en version.py
  * Modificar el Changelog en README
  * python setup.py doc
  * linguist
  * python setup.py doc
  * python setup.py install
  * python setup.py doxygen
  * git commit -a -m 'xulpymoney-version'
  * git push
  * Hacer un nuevo tag en GitHub
  * python setup.py sdist upload -r pypi
  * Crea un nuevo ebuild de Gentoo con la nueva versión
  * Subelo al repositorio del portage
  * Change to windows. Enter in an Administrator console.
  * Change to xulpymoney source directory and make git pull
  * python setup.py pyinstaller
  * Add file to github release
""")

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

#app=QCoreApplication(sys.argv)

#app.setOrganizationName("xulpymoney")
#app.setOrganizationDomain("xulpymoney.sourceforge.net")
#app.setApplicationName("xulpymoney")
#translator=QTranslator()
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

if platform.system()=="Linux":
    data_files=[
    ('/usr/share/pixmaps/', ['xulpymoney/images/xulpymoney.png']), 
    ('/usr/share/applications/', ['xulpymoney.desktop']), 
               ]
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
    description='Home and financial accounting system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 4 - Beta',
              'Intended Audience :: End Users/Desktop',
              'Topic :: Office/Business :: Financial :: Accounting',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Programming Language :: Python :: 3',
             ], 
    keywords='financial home accounting system',
    url='https://github.com/Turulomio/xulpymoney',
    author='Turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['xulpymoney'],
    entry_points = {'console_scripts': ['xulpymoney_init=xulpymoney.xulpymoney_init:main',
                                        'xulpymoney_bolsamadrid_client=xulpymoney.sources.bolsamadrid_client:main',
                                        'xulpymoney_google_client=xulpymoney.sources.google_client:main',
                                        'xulpymoney_infobolsa_client=xulpymoney.sources.infobolsa_client:main',
                                        'xulpymoney_morningstar_client=xulpymoney.sources.morningstar_client:main',
                                        'xulpymoney_quefondos_client=xulpymoney.sources.quefondos_client:main',
                                        'xulpymoney_run_client=xulpymoney.sources.run_client:main',
                                        'xulpymoney_yahoo_client=xulpymoney.sources.yahoo_client:main',
                                       ],
                    'gui_scripts': ['xulpymoney=xulpymoney.xulpymoney:main',
                                       ],
                },
    install_requires= [ 'setuptools',
                        'psycopg2', 
                        'pytz',
                        'officegenerator', 
                        'colorama', 
                        'python-stdnum',
                        'PyQtChart;platform_system=="Windows"',
                        'PyQt5;platform_system=="Windows"',
                        'pywin32;platform_system=="Windows"',
                        ], #PyQt5 and PyQtChart doesn't have egg-info in Gentoo, so I remove it to install it with ebuild without making 2 installations. Should be added manually when using pip to install
    data_files=data_files,
    cmdclass={
                        'doxygen': Doxygen,
                        'doc': Doc,
                        'uninstall':Uninstall, 
                        'compile': Compile, 
                        'procedure': Procedure,
                        'pyinstaller': PyInstaller,
                     },
    zip_safe=False,
    include_package_data=True
    )

