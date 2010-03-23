from docutils.parsers import rst
import docutils.parsers.rst.directives
from docutils.nodes import General, Inline, Element
import os, re

# hack(?) to point to source files
SRC_DIR = '.'

valid_controls = ['browser','burst_s5']

class video(General, Inline, Element):
    pass

class VideoDirective(rst.Directive):
    option_spec = {
        'video_mp4':docutils.parsers.rst.directives.path,
        'video_ogv':docutils.parsers.rst.directives.path,
        'loop':bool,
        'width':docutils.parsers.rst.directives.unchanged_required,
        'height':docutils.parsers.rst.directives.unchanged_required,
        'stdheight':docutils.parsers.rst.directives.unchanged_required,
        'controls':docutils.parsers.rst.directives.unchanged_required,
        }

    def run(self):
        # Create node(s).
        # Node list to return.
        node = video()

        node.options = self.options.copy()
        for key in self.option_spec.keys():
            # fixup paths
            if self.option_spec[key] != docutils.parsers.rst.directives.path:
                continue
            if key not in node.options:
                continue
            node.options[key] = os.path.join(SRC_DIR,node.options[key])

        # check for .mp4 video file
        if 'video_mp4' not in node.options:
            raise ValueError('video_mp4 option not specified')

        if not os.path.exists(node.options['video_mp4']):
            raise ValueError('video_mp4 "%s" specified, but does not exist (curdir: "%s")'%(
                node.options['video_mp4'], os.path.abspath(os.curdir)))

        if 'video_mp4' in node.options and 'video_ogv' not in node.options:
            ogv_fname = os.path.splitext(node.options['video_mp4'])[0] + '.ogv'
            if os.path.exists(ogv_fname):
                node.options['video_ogv'] = ogv_fname

        node_list = [node]
        return node_list

global id_count
id_count = 1

def simple_render( node ):
    global id_count
    v_id = 'video-%d'%id_count
    id_count += 1

    template = '<div %(classes)s>\n'

    controls = node.options.get('controls','browser')
    if controls not in valid_controls:
        raise ValueError('invalid controls option')

    browser_controls=controls=='browser'

    atts = []
    if browser_controls:
        atts.append( 'controls' )
    else:
        template += '<div class="docutils-video-controls">\n'
        template += '<input type="button" value="Play" onclick="document.getElementById(\'%(id)s\').play();">'
        template += '<input type="button" value="Pause" onclick="document.getElementById(\'%(id)s\').pause();">'
        template += '</div>\n'

    template += '<div class="docutils-video-player">\n'
    template += '<video %(atts)s id="%(id)s">\n'
    if 'video_mp4' in node.options:
        template += '  <source src="%(video_mp4)s" type="video/mp4"></source>\n'
    if 'video_ogv' in node.options:
        template += '  <source src="%(video_ogv)s" type="video/ogg"></source>\n'
    template += '  Sorry, your browser does not support the <pre>video</pre> tag.\n'
    template += '</video>\n'
    template += '</div>\n'

    node.setdefault('classes',[]).append('docutils-video-container')
    node.options['classes'] = 'class="' + ' '.join([c for c in node['classes']]) +'"'
    template += '</div>\n'

    node.options['id'] = v_id

    if node.options.get('loop',False):
        atts.append('loop')

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

def visit_video_html(self,node):
    html = simple_render( node )
    self.body.append(html)

def depart_video_html(self,node):
    pass

docutils.parsers.rst.directives.register_directive( 'video', VideoDirective )
