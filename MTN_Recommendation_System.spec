# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\MTN\\Recomendation_system\\Recommendation_Engine_Version_5.py'],
    pathex=[],
    binaries=[],
    datas=[('D:/MTN/Recomendation_system/New-mtn-logo.jpg', '.'), ('D:/MTN/Recomendation_system/SubscriberProfileData.csv', '.'), ('D:/MTN/Recomendation_system/ProductCatalogue.csv', '.'), ('D:/MTN/Recomendation_system/hackathon2025-454908-0a52f19ef9b1.json', '.')],
    hiddenimports=['PIL._tkinter_finder', 'pandas', 'vertexai', 'google.cloud.aiplatform'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MTN_Recommendation_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\MTN\\Recomendation_system\\mtn_icon.ico'],
)
