# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['xulpymoney.py'],
             pathex=['C:\\Users\\Vania\\Documents\\Proyectos\\xulpymoney'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='xulpymoney-0.7.0',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True ,
	  icon='xulpymoney\\images\\xulpymoney.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='xulpymoney-0.7.0')
