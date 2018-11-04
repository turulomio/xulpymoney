What is RecPermissions
======================
It's a script to change Linux permissions and ownership in one step. It can delete empty directories when necessary.

Usage
=====

Here you have a console video example:

![English howto](https://raw.githubusercontent.com/Turulomio/recpermissions/master/doc/ttyrec/recpermissions_howto_en.gif)

Once installed, you can see man documentation with

`man recpermissions`

License
=======
GPL-3

Links
=====

Source code & Development:
    https://github.com/Turulomio/recpermissions

Doxygen documentation:
    http://turulomio.users.sourceforge.net/doxygen/recpermissions/

Main developer web page:
    http://turulomio.users.sourceforge.net/en/proyectos.html
    
Pypi web page:
    https://pypi.org/project/recpermissions/

Gentoo ebuild
    You can find a Gentoo ebuild in https://sourceforge.net/p/xulpymoney/code/HEAD/tree/myportage/app-admin/recpermissions/


Dependencies
============
* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.

Changelog
=========
1.3.0
  * If file owner isn't in /etc/passwd now remains its uid, and desn't crash
  * Code of conduct is added to the project
  * Added localized integers in summary
  * Added files to french translation
  * Added --only parameter funcionality to allow change ownership and permissions of one file or directory

1.2.0
  * Due to a boolean logic error, some changes didn't took place

1.1.0
  * Added 30 seconds to reload video in howto.py
  * Nothing is changed if --user --group --files or --directories is not set.

1.0.0
  * Version fully operational
  * Added howto video in English and Spanish
  * Man pages and spanish translation have been improved
  * Added summary and added io error exception catching

0.2.1
  * Solved critical bug. Directory now is set tu absolut_path parameter

0.2.0
  * Added absolute path parameter to avoid errors and wrong changes

0.1.1
  * Solved bug in current path directory

0.1.0
  * Creating infrastructure
