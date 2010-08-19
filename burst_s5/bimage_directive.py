from docutils.parsers import rst
import docutils.parsers.rst.directives
from docutils.nodes import General, Inline, Element
import os, re

# hack(?) to point to source files
SRC_DIR = '.'

class bimage(General, Inline, Element):
    pass

class BimageDirective(rst.Directive):
    option_spec = {
        'file':docutils.parsers.rst.directives.path,
        'width':docutils.parsers.rst.directives.unchanged_required,
        'height':docutils.parsers.rst.directives.unchanged_required,
        'stdheight':docutils.parsers.rst.directives.unchanged_required,
        }

    def run(self):
        # Create node(s).
        # Node list to return.
        node = bimage()

        node.options = self.options.copy()
        for key in self.option_spec.keys():
            # fixup paths
            if self.option_spec[key] != docutils.parsers.rst.directives.path:
                continue
            if key not in node.options:
                continue
            node.options[key] = os.path.join(SRC_DIR,node.options[key])

        # check for bimage file
        if 'file' not in node.options:
            raise ValueError('file option not specified')

        if not os.path.exists(node.options['file']):
            raise ValueError('file "%s" specified, but does not exist (curdir: "%s")'%(
                node.options['file'], os.path.abspath(os.curdir)))

        node_list = [node]
        return node_list

global id_count
id_count = 1

def simple_render( node ):
    global id_count
    v_id = 'bimage-%d'%id_count
    id_count += 1

    template = '<div %(classes)s>\n'

    atts = []

    template += '  <img src="%(file)s" %(atts)s %(id)s />\n'

    node.setdefault('classes',[]).append('docutils-bimage-container')
    node.options['classes'] = 'class="' + ' '.join([c for c in node['classes']]) +'"'
    template += '</div>\n'

    node.options['id'] = v_id

    if 'height' in node.options and 'stdheight' in node.options:
        raise ValueError('"height" and "stdheight" options may not be simultaneously specified')
    if 'width' in node.options and 'stdheight' in self.options:
        raise ValueError('"width" and "stdheight" options may not be simultaneously specified')

    if 'stdheight' in node.options:
        zheight = float(node.options['stdheight'])
        STD_HEIGHT = 600.0
        target_height = float(os.environ.get('BURST_S5_HEIGHT',STD_HEIGHT))
        frac = zheight/STD_HEIGHT # fraction of standard height

        height = frac*target_height

        node.options['height'] = height
        del node.options['stdheight']

    for att in ['width','height']:
        if att in node.options:
            atts.append('%s="%s"'%(att,node.options[att]))

    node.options['atts'] = ' '.join(atts)
    html = template % node.options
    return html

#monkey patches to docutils (I guess this is how plugins work)

def visit_bimage_html(self,node):
    html = simple_render( node )
    self.body.append(html)

def depart_bimage_html(self,node):
    pass

docutils.parsers.rst.directives.register_directive( 'bimage', BimageDirective )
