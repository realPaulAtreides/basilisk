import setuptools

setuptools.setup(
    name='basilisk',
    version='0.0.1',
    packages=['basilisk'],
    license='MIT',
    descriptions='Python rpc proxy for grin-wallet owner api',
    author='paul atreides',
    install_requires=['jsonrpcclient[requests]', 'ecdsa', 'pycryptodome']
)
