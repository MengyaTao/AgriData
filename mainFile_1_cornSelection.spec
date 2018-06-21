# -*- mode: python -*-
import sys
sys.setrecursionlimit(5000)
block_cipher = None


a = Analysis(['mainFile_1_cornSelection.py'],
             pathex=['C:\\Users\\mtao.ESM.001\\Box Sync\\PhD_Thesis_materials\\Scripts\\aghist_v7'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='mainFile_1_cornSelection',
          debug=False,
          strip=False,
          upx=True,
          console=False )
