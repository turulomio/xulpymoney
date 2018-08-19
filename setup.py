from xulpymoney import __version__
from setuptools import setup, Command
from mangenerator import Man

import datetime
import gettext
import os
import platform
import site

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
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("cp ttyrec/xulpymoney_howto_en.gif html")#Copies images
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/xulpymoney/ --delete-after")
        os.chdir("..")

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
            os.system("rm /usr/bin/xulpymoney")
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
        #es
        os.system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o locale/xulpymoney.pot *.py xulpymoney/*.py doc/ttyrec/*.py")
        os.system("msgmerge -N --no-wrap -U locale/es.po locale/xulpymoney.pot")
        os.system("msgfmt -cv -o xulpymoney/locale/es/LC_MESSAGES/xulpymoney.mo locale/es.po")

    ########################################################################

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

if platform.system()=="Linux":
    data_files=[
    #('/usr/share/man/man1/', ['man/man1/xulpymoney.1']), 
    #            ('/usr/share/man/es/man1/', ['man/es/man1/xulpymoney.1'])
               ]
else:
    data_files=[]

setup(name='xulpymoney',
     version=__version__,
     description='Personal and finances accounting system',
     long_description=long_description,
     long_description_content_type='text/markdown',
     classifiers=['Development Status :: 4 - Beta',
                  'Intended Audience :: Developers',
                  'Topic :: Software Development :: Build Tools',
                  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                  'Programming Language :: Python :: 3',
                 ], 
     keywords='personal accounting',
     url='https://xulpymoney.sourceforge.io/',
     author='Turulomio',
     author_email='turulomio@yahoo.es',
     license='GPL-3',
     packages=['xulpymoney'],
     entry_points = {'console_scripts': ['xulpymoney=xulpymoney.xulpymoney:main',
                                        ],
                    },
     install_requires=['colorama','mangenerator','setuptools','ttyrecgenerator'],
     data_files=data_files,
     cmdclass={
        'doxygen': Doxygen,
        'doc': Doc,
        'uninstall':Uninstall, 
             },
      zip_safe=False,
      include_package_data=True
     )


"""
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
#!/usr/bin/python3
import argparse
import datetime
import os
import sys
import platform
from subprocess import call, check_call
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from libxulpymoneyversion import version

def shell(*args):
    print(" ".join(args))
    call(args,shell=True)

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
    


if __name__ == '__main__':
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='Makefile.py', description='Makefile in python', epilog="Developed by Mariano Muñoz", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--doc', help="Generate user documentation and internationalization files",action="store_true",default=False)
    parser.add_argument('--doxygen', help="Generate api documentation with doxygen",action="store_true",default=False)
    parser.add_argument('--compile', help="App compilation",action="store_true",default=False)
    parser.add_argument('--compile_images', help="App compilation",action="store_true",default=False)
    parser.add_argument('--destdir', help="Directory to install",action="store",default="/")
    parser.add_argument('--uninstall', help="Uninstall",action="store_true",default=False)
    parser.add_argument('--dist_sources', help="Make a sources tar", action="store_true",default=False)
    parser.add_argument('--dist_linux', help="Make a Linux binary distribution", action="store_true",default=False)
    parser.add_argument('--dist_windows', help="Make a Windows binary distribution", action="store_true",default=False)
    parser.add_argument('--python', help="Python path", action="store",default='/usr/bin/python3')
    args=parser.parse_args()

    prefixbin=args.destdir+"/usr/bin"
    prefixlib=args.destdir+"/usr/lib/xulpymoney"
    prefixshare=args.destdir+"/usr/share/xulpymoney"
    prefixpixmaps=args.destdir+"/usr/share/pixmaps"
    prefixapplications=args.destdir+"/usr/share/applications"   

    if args.doc==True:
        shell("pylupdate5 -noobsolete -verbose xulpymoney.pro")
        shell("lrelease xulpymoney.pro")
    elif args.uninstall==True:
        shell("rm " + prefixbin + "/xulpymoney*")
        shell("rm -Rf " + prefixlib)
        shell("rm -Rf " + prefixshare)
        shell("rm -fr " + prefixpixmaps + "/xulpymoney.png")
        shell("rm -fr " + prefixapplications +"/xulpymoney.desktop")
    elif args.doxygen==True:
        os.chdir("doc")
        shell("doxygen Doxyfile")
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/xulpymoney/ --delete-after")
        os.chdir("..")
    elif args.dist_sources==True:
        shell("{} setup.py sdist".format(args.python))
    elif args.dist_linux==True:
        shell("{} setup.py build_exe".format(args.python))    
        print (build_dir(), filename_output(), os.getcwd())
        pwd=os.getcwd()
        os.chdir(build_dir())
        print (build_dir(), filename_output(), os.getcwd())
        os.system("tar cvz -f '{0}/dist/{1}.tar.gz' * -C '{0}/{2}/'".format(pwd, filename_output(),  build_dir()))
    elif args.dist_windows==True:
        if platform.system()=="Windows":
            check_call([sys.executable, "setup.py","bdist_msi"])
            #        os.chdir(build_dir())
            #        inno="c:/Program Files (x86)/Inno Setup 5/ISCC.exe"
            ##    if platform.architecture()[0]=="32bit":
            ##        inno=inno.replace(" (x86)", "")
            #
            #        check_call([inno,  "/o../",  "/DVERSION_NAME={}".format(version_windows()), "/DFILENAME={}".format(filename_output()),"xulpymoney.iss"], stdout=sys.stdout)
        else:
            print("You need to launch this script in a Windows environment")
    elif args.compile_images==True:
        shell("pyrcc5 images/xulpymoney.qrc -o images/xulpymoney_rc.py")
    elif args.compile==True:
        futures=[]
        with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
            futures.append(executor.submit(shell, "pyuic5 ui/frmAbout.ui -o ui/Ui_frmAbout.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmAccess.ui -o ui/Ui_frmAccess.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmDPSAdd.ui -o ui/Ui_frmDPSAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmHelp.ui -o ui/Ui_frmHelp.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmInit.ui -o ui/Ui_frmInit.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmMain.ui -o ui/Ui_frmMain.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSplit.ui -o ui/Ui_frmSplit.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSplitManual.ui -o ui/Ui_frmSplitManual.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmAccountOperationsAdd.ui -o ui/Ui_frmAccountOperationsAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmAuxiliarTables.ui -o ui/Ui_frmAuxiliarTables.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgBanks.ui -o ui/Ui_wdgBanks.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgCalculator.ui -o ui/Ui_wdgCalculator.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgConcepts.ui -o ui/Ui_wdgConcepts.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgConceptsHistorical.ui -o ui/Ui_wdgConceptsHistorical.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgAccounts.ui -o ui/Ui_wdgAccounts.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgDisReinvest.ui -o ui/Ui_wdgDisReinvest.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmAccountsReport.ui -o ui/Ui_frmAccountsReport.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestmentClasses.ui -o ui/Ui_wdgInvestmentClasses.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgDividendsReport.ui -o ui/Ui_wdgDividendsReport.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgAPR.ui -o ui/Ui_wdgAPR.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgIndexRange.ui -o ui/Ui_wdgIndexRange.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestments.ui -o ui/Ui_wdgInvestments.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestmentsRanking.ui -o ui/Ui_wdgInvestmentsRanking.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgLastCurrent.ui -o ui/Ui_wdgLastCurrent.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgOpportunities.ui -o ui/Ui_wdgOpportunities.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgOpportunitiesAdd.ui -o ui/Ui_wdgOpportunitiesAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgOrders.ui -o ui/Ui_wdgOrders.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgOrdersAdd.ui -o ui/Ui_wdgOrdersAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmDividendsAdd.ui -o ui/Ui_frmDividendsAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmInvestmentReport.ui -o ui/Ui_frmInvestmentReport.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmInvestmentOperationsAdd.ui -o ui/Ui_frmInvestmentOperationsAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSellingPoint.ui -o ui/Ui_frmSellingPoint.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSettings.ui -o ui/Ui_frmSettings.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmCreditCardsAdd.ui -o ui/Ui_frmCreditCardsAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmTransfer.ui -o ui/Ui_frmTransfer.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSharesTransfer.ui -o ui/Ui_frmSharesTransfer.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgTotal.ui -o ui/Ui_wdgTotal.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmProductReport.ui -o ui/Ui_frmProductReport.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmQuotesIBM.ui -o ui/Ui_frmQuotesIBM.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSelector.ui -o ui/Ui_frmSelector.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmEstimationsAdd.ui -o ui/Ui_frmEstimationsAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgCuriosity.ui -o ui/Ui_wdgCuriosity.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgCuriosities.ui -o ui/Ui_wdgCuriosities.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgDatetime.ui -o ui/Ui_wdgDatetime.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgProductHistoricalChart.ui -o ui/Ui_wdgProductHistoricalChart.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgProducts.ui -o ui/Ui_wdgProducts.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgQuotesUpdate.ui -o ui/Ui_wdgQuotesUpdate.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgSimulations.ui -o ui/Ui_wdgSimulations.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgSimulationsAdd.ui -o ui/Ui_wdgSimulationsAdd.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestmentsOperations.ui -o ui/Ui_wdgInvestmentsOperations.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgMergeCodes.ui -o ui/Ui_wdgMergeCodes.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgYearMonth.ui -o ui/Ui_wdgYearMonth.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/wdgYear.ui -o ui/Ui_wdgYear.py"))
    else:
        shell("install -o root -d "+ prefixbin)
        shell("install -o root -d "+ prefixlib)
        shell("install -o root -d "+ prefixshare)
        shell("install -o root -d "+ prefixshare+"/sql")
        shell("install -o root -d "+ prefixpixmaps)
        shell("install -o root -d "+ prefixapplications)

        shell("install -m 755 -o root xulpymoney.py "+ prefixbin+"/xulpymoney")
        shell("install -m 755 -o root xulpymoney_init.py "+ prefixbin+"/xulpymoney_init")
        shell("install -m 755 -o root xulpymoney_simulation_indexrange.py "+ prefixbin+"/xulpymoney_simulation_indexrange")
        shell("install -m 755 -o root sources/morningstar_client.py "+ prefixbin+"/xulpymoney_morningstar_client")
        shell("install -m 755 -o root sources/infobolsa_client.py "+ prefixbin+"/xulpymoney_infobolsa_client")
        shell("install -m 755 -o root sources/bolsamadrid_client.py "+ prefixbin+"/xulpymoney_bolsamadrid_client")
        shell("install -m 755 -o root sources/quefondos_client.py " + prefixbin+"/xulpymoney_quefondos_client")
        shell("install -m 755 -o root sources/yahoo_client.py " + prefixbin+"/xulpymoney_yahoo_client")
        shell("install -m 755 -o root sources/google_client.py " + prefixbin+"/xulpymoney_google_client")
        shell("install -m 755 -o root sources/run_client.py "+ prefixbin+"/xulpymoney_run_client")
        shell("install -m 755 -o root test/xulpymoney_test.py "+ prefixbin+"/xulpymoney_test")
        shell("install -m 644 -o root ui/*.py lib*.py images/*.py "+ prefixlib)
        shell("install -m 644 -o root i18n/*.qm " + prefixlib)
        shell("install -m 644 -o root sources/*.py "+ prefixlib)
        shell("install -m 644 -o root xulpymoney.desktop "+ prefixapplications)
        shell("install -m 644 -o root images/coins.png "+ prefixpixmaps+"/xulpymoney.png")
        shell("install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt "+ prefixshare)
        shell("install -m 644 -o root sql/xulpymoney.sql "+ prefixshare+"/sql")
        shell("install -m 644 -o root odf/report.odt "+ prefixshare)
    print ("*** Process took {} using {} processors ***".format(datetime.datetime.now()-start , cpu_count()))
"""