from distutils.core import setup

setup(
    name='django-contactfield',
    version='0.0.2',
    author='Colin Barnwell',
    packages=['contactfield'],
    description='Customisable contact field for Django',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.4",
        "django-jsonfield==0.9.12b1"
    ],
)
