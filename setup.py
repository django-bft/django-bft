from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-bft',
    version=__import__('bft').__version__,
    description='Big File Transfer Application written in Django',
    long_description=open('docs/source/index.rst').read(),
    author='Jay McEntire',
    author_email='jay.mcentire@gmail.com',
    url='http://github.com/django-bft/dango-bft',
    download_url='https://github.com/django-bft/dango-bft/downloads',
    license='GNU GPL v3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False, # because we're including media that Django needs
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)