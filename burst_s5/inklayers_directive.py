from docutils.parsers import rst
import docutils.parsers.rst.directives
from docutils.nodes import General, Inline, Element
import os, re, copy, sys, stat
from lxml import etree # Ubuntu Karmic package: python-lxml
import subprocess, tempfile

# hack(?) to point to source files
SRC_DIR = '.'

CACHE_PREFIX = '.inklayers-'
valid_modes = ['overlay', 'replace']

# Where is the inkscape command?
if sys.platform.startswith('darwin'):
    INKSCAPE = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
else:
    # It's on the path
    INKSCAPE = 'inkscape'

def get_stdout(cmd):
    """call a command and return the stdout, raising exception if error"""
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    sys.stdout.write('calling "%s"...'%(' '.join(cmd)))
    sys.stdout.flush()
    p.wait()
    if p.returncode != 0:
        raise RuntimeError('command "%s" failed with code %d'%(
                ' '.join(cmd), p.returncode))
    sys.stdout.write('OK\n')
    sys.stdout.flush()
    return p.stdout.read()

def get_width_height( fname, orig_modtime=None ):
    """get (possibly cached) width and height of .svg file with inkscape"""
    # compute filename of cached width/height
    wh_cache_path, wh_cache_fname = os.path.split(fname)
    wh_cache_fname = CACHE_PREFIX+os.path.splitext(wh_cache_fname)[0]+'.txt'
    wh_cache_fname = os.path.join( wh_cache_path, wh_cache_fname )

    # read cache if it exists
    if os.path.exists( wh_cache_fname ):
        modtime = os.stat(wh_cache_fname)[stat.ST_MTIME]
        if orig_modtime is None:
            orig_modtime = os.stat(fname)[stat.ST_MTIME]
        if modtime > orig_modtime:
            width,height = open( wh_cache_fname ).read().strip().split()
            return width,height

    # no cache, query inkscape for information
    tmpf = tempfile.NamedTemporaryFile(suffix='.png')
    tmpf.close()
    cmd = [INKSCAPE,'-C',fname,'-e',tmpf.name]
    get_stdout(cmd)
    import Image
    # XXX TODO: convert to reading XML file instead of using PIL
    im = Image.open(tmpf.name)
    (width, height) = im.size
    os.unlink(tmpf.name)

    fd = open (wh_cache_fname,mode="w")
    fd.write("%s %s\n"%(width,height))
    fd.close()
    return width, height

class inklayers(General, Inline, Element):
    pass

class InklayersDirective(rst.Directive):
    """convert a multi-layered Inkscape .svg file into an incremental slide"""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True # allow filenames with spaces

    option_spec = {
        'mode':docutils.parsers.rst.directives.unchanged_required,
        'width':docutils.parsers.rst.directives.unchanged_required,
        'height':docutils.parsers.rst.directives.unchanged_required,
        'stdheight':docutils.parsers.rst.directives.unchanged_required,
        }

    def run(self):
        # Create node(s).
        node = inklayers()
        fname = self.arguments[0]
        if not os.path.exists(fname):
            raise ValueError('filename "%s" does not exist'%fname)
        node.src = fname

        if 'mode' in self.options:
            found = 0
            for valid_mode in valid_modes:
                if valid_mode.startswith(self.options['mode'].lower()):
                    found += 1
                    use_mode = valid_mode
            if found != 1:
                raise ValueError('"mode" option matched %d times'%found)
            node.mode = use_mode
        else:
            node.mode = 'overlay'

        node.options = {}
        for name in ['width','height','stdheight']:
            if name in self.options:
                node.options[name] = self.options[name]

        if 'height' in self.options and 'stdheight' in self.options:
            raise ValueError('"height" and "stdheight" options may not be simultaneously specified')
        if 'width' in self.options and 'stdheight' in self.options:
            raise ValueError('"width" and "stdheight" options may not be simultaneously specified')

        node_list = [node]
        return node_list

def visit_inklayers_html(self,node):
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

    # output .png images in new path
    out_dir = 'inklayers' + os.environ.get('BURST_S5_INKLAYERS_SUFFIX','')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    out_base_fname = os.path.split(orig_fname)[-1]
    out_base_fname = os.path.splitext(out_base_fname)[0]
    out_base_fname = os.path.join( out_dir, out_base_fname )

    # but .svg files must remain alongside originals to maintain links
    svg_base_path, svg_base_fname = os.path.split(orig_fname)
    svg_base_fname = CACHE_PREFIX + os.path.splitext(svg_base_fname)[0]
    svg_base_fname = os.path.join( svg_base_path, svg_base_fname )

    source_fname = orig_fname
    image_fnames = []


    srcwidth, srcheight = get_width_height( source_fname, orig_modtime )
    STD_HEIGHT = 600.0 # height of slide div in 1024x768
    STD_DPI = 90.0
    target_height = float(os.environ.get('BURST_S5_HEIGHT',STD_HEIGHT))
    max_width = float(os.environ.get('BURST_S5_MAX_WIDTH',STD_HEIGHT*1.667)) # aspect of slide div in 1024x768

    if 'stdheight' in node.options:
        zheight = float(node.options['stdheight'])
        frac = zheight/STD_HEIGHT # fraction of standard height

        height = frac*target_height

        scale = height/float(srcheight)
        width = float(srcwidth)*scale
        if width> max_width:
            newscale = max_width/width
            width *= newscale
            height *= newscale
            scale *= newscale

        width = int(round(width))
        height = int(round(height))
        node.options['width'] = width
        node.options['height'] = height
        dpi = str(STD_DPI*scale)
    else:
        width = node.options.get('width',srcwidth)
        height = node.options.get('height',srcheight)
        dpi = str(STD_DPI)

    for i,layer_id in enumerate(layer_ids):
        out_fname = out_base_fname + layer_id + '.png'
        image_fnames.append( out_fname )

        skip_png = False
        if os.path.exists(out_fname):
            modtime = os.stat(out_fname)[stat.ST_MTIME]
            if modtime > orig_modtime:
                skip_png = True

        if skip_png:
            continue

        if node.mode == 'overlay':
            cmd_extra = ['-i',layer_id]
        elif node.mode == 'replace':
            out_svg_fname = svg_base_fname + '-' + layer_id + '.svg'

            skip_svg = False
            if os.path.exists(out_svg_fname):
                modtime = os.stat(out_svg_fname)[stat.ST_MTIME]
                if modtime > orig_modtime:
                    skip_svg = True

            if not skip_svg:
                newroot = copy.deepcopy(root)

                # remove undisplayed layers
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

                # turn on all layers (sometimes files are saved with layers turned off)
                elems = newroot.findall(tag_name)
                for child in elems:
                    if 'style' in child.attrib:
                        del child.attrib['style']

                etree.ElementTree(newroot).write( out_svg_fname )

            source_fname = out_svg_fname
            cmd_extra = [
                '-b','white',  # white background
                '-y','0xFF',   # fully opaque
                ]

        cmd = [INKSCAPE,
               '-j',          # only export this layer
               '-C',          # export canvas (page)
               '-d', dpi,
               source_fname,
               '-e',out_fname,
               ] + cmd_extra
        get_stdout(cmd)

    if 1:
        # export all layers for handout
        out_fname = out_base_fname + '.png'
        skip_final_png = False
        if os.path.exists(out_fname):
            modtime = os.stat(out_fname)[stat.ST_MTIME]
            if modtime > orig_modtime:
                skip_final_png = True

        if not skip_final_png:
            cmd = [INKSCAPE,
                   '-C',          # export canvas (page)
                   '-d', dpi,
                   source_fname,
                   '-e',out_fname,
                   ]
            get_stdout(cmd)
        image_fnames.append( out_fname )

    html = ('<div class="animation container inklayers" '
            'style="width: %spx; height: %spx;">\n'%(width,height))
    for i,image_fname in enumerate( image_fnames ):
        classes = []
        if i != 0:
            classes.append('incremental')

        # This is slightly different than docutils documentation
        #  suggests: make each layer in incremental, hidden and
        #  slide-display classes, but have an extra render of all
        #  layers than is only displayed in the handout.

        if i != len(image_fnames)-1:
            classes.append('hidden')
            classes.append('slide-display')
        else:
            classes = ['handout']
        if len(classes):
            class_str = ' class="%s"'%( ' '.join(classes), )
        else:
            class_str = ''

        atts = []
        for name in ['width','height']:
            if name in node.options:
                atts.append( '%s="%s"'%(name,node.options[name]))
        if len(atts):
            atts_str = ' ' + ' '.join(atts)
        else:
            atts_str = ''

        html += '  <img%s%s src="%s" alt="%s">\n'%(class_str,atts_str,
                                                   image_fname,
                                                   image_fname)
    html += '</div>'

    self.body.append(html)

def depart_inklayers_html(self,node):
    pass

docutils.parsers.rst.directives.register_directive( 'inklayers', InklayersDirective )
