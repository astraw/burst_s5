from docutils.parsers import rst
import docutils.parsers.rst.directives
from docutils.nodes import General, Inline, Element
import os, re, copy, sys, stat
from lxml import etree # Ubuntu Karmic package: python-lxml
import subprocess, tempfile

# hack(?) to point to source files
SRC_DIR = '.'

# Where is the inkscape command?
if sys.platform.startswith('darwin'):
    INKSCAPE = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
else:
    # It's on the path
    INKSCAPE = 'inkscape'

class inkslide(General, Inline, Element):
    pass

class InkslideDirective(rst.Directive):
    """convert a multi-layered Inkscape .svg file into an incremental slide"""
    option_spec = {
        'src':docutils.parsers.rst.directives.path,
        }

    def run(self):
        # Create node(s).
        # Node list to return.
        node = inkslide()
        node.src = self.options['src']
        node_list = [node]
        return node_list

def visit_inkslide_html(self,node):
    orig_fname = os.path.join(SRC_DIR,node.src)
    orig_modtime = os.stat(orig_fname)[stat.ST_MTIME]
    root = etree.parse(orig_fname).getroot()
    tag_name = '{http://www.w3.org/2000/svg}g'
    attrib_key = '{http://www.inkscape.org/namespaces/inkscape}groupmode'
    label_key = '{http://www.inkscape.org/namespaces/inkscape}label'
    layer_ids = []
    for child in root:
        if child.tag == tag_name:
            if child.attrib.get(attrib_key,None) == 'layer':
                label = child.attrib[label_key]
                layer_ids.append( child.attrib['id'] )
    out_dir = 'svg-slide-output'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    out_base_fname = os.path.split(orig_fname)[-1]
    out_base_fname = os.path.splitext(out_base_fname)[0]
    out_base_fname = os.path.join( out_dir, out_base_fname )
    image_fnames = []
    mode = 'cumulative layers'
    for i,layer_id in enumerate(layer_ids):
        if mode == 'single layer':
            source_fname = orig_fname
            cmd_extra = ['-i',layer_id, '-j'] # layer id
        elif mode == 'cumulative layers':
            out_svg_fname = out_base_fname + layer_id + '.svg'

            skip = False
            if os.path.exists(out_svg_fname):
                modtime = os.stat(out_svg_fname)[stat.ST_MTIME]
                if modtime > orig_modtime:
                    skip = True

            if not skip:
                newroot = copy.deepcopy(root)
                elems = newroot.findall(tag_name)
                for remove_layer_id in layer_ids[i+1:]:
                    removed = False
                    for child in elems:
                        if (child.attrib.get(attrib_key,None) == 'layer' and
                            child.attrib['id'] == remove_layer_id):
                            newroot.remove( child )
                            removed = True
                            break
                    if not removed:
                        raise ValueError('could not remove layer_id "%s"'%remove_layer_id)
                etree.ElementTree(newroot).write( out_svg_fname )

            source_fname = out_svg_fname
            cmd_extra = []
        out_fname = out_base_fname + layer_id + '.png'

        skip = False
        if os.path.exists(out_fname):
            modtime = os.stat(out_fname)[stat.ST_MTIME]
            if modtime > orig_modtime:
                skip = True

        if not skip:
            cmd = [INKSCAPE,
                   '-j',          # only export this layer
                   '-C',          # export canvas (page)
                   source_fname,
                   '-e',out_fname,
                   ] + cmd_extra
            subprocess.check_call(cmd)
        image_fnames.append( out_fname )
    html = '<div class="animation container">\n'
    for i,image_fname in enumerate( image_fnames ):
        classes = []
        if i != 0:
            classes.append('incremental')
        if i != len(image_fnames)-1:
            classes.append('hidden')
            classes.append('slide-display')
        if len(classes):
            class_str = ' class="%s"'%( ' '.join(classes), )
        else:
            class_str = ''
        html += '  <img%s src="%s" alt="%s">\n'%(class_str,
                                                 image_fname,
                                                 image_fname)
    html += '</div>'

    self.body.append(html)

def depart_inkslide_html(self,node):
    pass

docutils.parsers.rst.directives.register_directive( 'inkslide', InkslideDirective )
