from distutils.core import setup

setup(
    name='django-contactfield',
    version='1.0.0',
    author='Colin Barnwell',
    packages=['contactfield', 'contactfield.templatetags'],
    description='Customisable contact field for Django',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.4",
        "django-jsonfield==1.4.1"
    ],
)
