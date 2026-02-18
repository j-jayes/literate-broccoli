from setuptools import find_packages, setup

setup(
    name='literate-broccoli',
    version='1.0.0',
    description='Office Lunch Ordering Microservice',
    author='Your Team',
    author_email='team@example.com',
    url='https://github.com/j-jayes/literate-broccoli',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9',
    install_requires=[
        'fastapi>=0.109.0',
        'uvicorn[standard]>=0.27.0',
        'sqlalchemy>=2.0.25',
        'pydantic>=2.5.3',
        'beautifulsoup4>=4.12.3',
        'redis>=5.0.1',
        'azure-identity>=1.15.0',
        'botbuilder-core>=4.15.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.4',
            'black>=23.12.1',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
        ],
        'docs': [
            'mkdocs>=1.5.3',
            'mkdocs-material>=9.5.3',
        ],
    },
    entry_points={
        'console_scripts': [
            'lunch-ordering=src.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
