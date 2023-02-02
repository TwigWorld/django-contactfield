from distutils.core import setup

setup(
    name='django-contactfield',
    version='2.0.0',
    author='Colin Barnwell',
    packages=['contactfield', 'contactfield.templatetags'],
    description='Customisable contact field for Django',
    long_description=open('README.md').read(),
    python_requires='>=3.7.0',
    install_requires=[
        "Django>=1.11, <2.0",
        "django-jsonfield==1.4.1"
    ],
    extras_require={
        "testing": [
            "pytest",
            "pytest-django",
        ]
    },
)
