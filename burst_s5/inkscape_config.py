import sys

# Where is the inkscape command?
if sys.platform.startswith('darwin'):
    INKSCAPE = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
else:
    # It's on the path
    INKSCAPE = 'inkscape'

tag_name = '{http://www.w3.org/2000/svg}g'
attrib_key = '{http://www.inkscape.org/namespaces/inkscape}groupmode'
label_key = '{http://www.inkscape.org/namespaces/inkscape}label'
