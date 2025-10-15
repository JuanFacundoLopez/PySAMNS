# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img/*', 'img/'),
        ('funciones/*.py', 'funciones/'),
        ('ventanas/*.py', 'ventanas/'),
        ('estilos.qss', '.')
    ],
    hiddenimports=[
        'numpy',
        'scipy',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pyqtgraph',
        'pyaudio',
        'sounddevice',
        'soundfile',
        'pandas',
        'sqlite3',
        'matplotlib',
        'scipy.signal',
        'scipy.fftpack',
        'numpy.core._dtype_ctypes',
        'pyqtgraph.graphicsItems.PlotDataItem',
        'pyqtgraph.graphicsItems.PlotCurveItem',
        'pyqtgraph.graphicsItems.ViewBox',
        'pyqtgraph.graphicsItems.GraphicsLayout',
        'pyqtgraph.graphicsItems.GraphicsLayout.GraphicsLayout',
        'pyqtgraph.graphicsItems.GraphicsWidget.GraphicsWidget',
        'pyqtgraph.graphicsItems.PlotItem',
        'pyqtgraph.graphicsItems.ViewBox.ViewBox',
        'pyqtgraph.graphicsItems.GraphicsItem',
        'pyqtgraph.graphicsItems.GraphicsObject',
        'pyqtgraph.graphicsItems.GraphicsWidget'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib.tests', 'numpy.random._examples'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PySAMNS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='img/Logocintra.ico',
    onefile=True
)
