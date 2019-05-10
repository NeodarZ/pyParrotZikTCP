import glob
import sys

if sys.platform == "win32":
    import py2exe
    from distutils.core import setup
else:
    from setuptools import setup


setup(
    name='parrotzikserver',
    description='Parrot Zik Tray Indicator',
    author="Dmitry Moiseev",
    author_email="m0sia@m0sia.ru",
    maintainer_email="m0sia@m0sia.ru",
    url="https://github.com/m0sia/pyParrotZik",
    license="'GPLv2+'",
    version='0.3',

    windows=[
        {
            'script': 'parrot_zik/test_server.py',
        }
    ],

    options={
        'py2exe': {
            #'packages':'encodings',
            # Optionally omit gio, gtk.keysyms, and/or rsvg if you're not using them
            'includes': 'cairo, pango, pangocairo, atk, gobject, gio, gtk.keysyms, _winreg',
            'dll_excludes': ['MSVCP90.dll', 'wbtapi.dll', 'irprops.cpl', 'crypt32.dll', 'MSIMG32.DLL', 'NSI.DLL', 'USP10.DLL', 'DNSAPI.DLL']        }
    },

    install_requires=[
        'beautifulsoup4', 'pybluez', 'dbus-python', 'twisted'
    ],

    packages=['parrot_zik', 'parrot_zik.interface', 'parrot_zik.indicator', 'parrot_zik.model'],
    entry_points={
        'console_scripts': [
            'parrot_zik_srv=parrot_zik.test_server:ParrotZik.main',
        ]
    },
    include_package_data=True,
)
