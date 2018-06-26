import setuptools

setuptools.setup(name='audio dropout detector',
                 version='0.1',
                 description='A package that can detect a dropout or glitch in a wav file',
                 long_description=open('README.md').read(),
                 url='http://github.com/johnblatchford/audio_dropout_detector',
                 author='John Blatchford',
                 author_email='listening@mac.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 zip_safe=False,
                 install_requires=[
                     'numpy',
                     'scipy',
                     'matplotlib',
                     'pytest',
                 ],
                 )
