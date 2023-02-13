from distutils.core import setup

setup(
    name='django-contactfield',
    version='2.0.0',
    author='Colin Barnwell',
    packages=['contactfield', 'contactfield.templatetags'],
    description='Customisable contact field for Django',
    long_description=open('README.md').read(),
    install_requires=[
        "django<3",
        "django-jsonfield"
    ],
    extras_require={
        "testing": [
            "pytest",
            "pytest-django",
        ]
    },
)
