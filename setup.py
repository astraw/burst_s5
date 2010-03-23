from distutils.core import setup

setup(name='burst_s5',
      version='0.0.1',
      license='MIT',
      packages=['burst_s5'],
      scripts=['scripts/burst2s5',
               'scripts/svg-images-abs2rel',
               'scripts/svg-images-copy-local',
               'scripts/svg-get-size',
               ],
      description='standards-compliant HTML slideshows with HTML5 video and Inkscape',
      )
