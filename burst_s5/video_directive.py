from docutils.parsers import rst
import docutils.parsers.rst.directives
from docutils.nodes import General, Inline, Element
import os, re

# hack(?) to point to source files
SRC_DIR = '.'

class video(General, Inline, Element):
    pass

class VideoDirective(rst.Directive):
    option_spec = {
        'mode':docutils.parsers.rst.directives.unchanged_required,
        'video_mp4':docutils.parsers.rst.directives.path,
        'video_ogv':docutils.parsers.rst.directives.path,
        'loop':bool,
        'width':int,
        'height':int,
        'height_short':int,
        'poster_jpg':docutils.parsers.rst.directives.path,
        'flash_swf':docutils.parsers.rst.directives.path,
        'title':docutils.parsers.rst.directives.unchanged_required,
        }

    def run(self):
        # Create node(s).
        # Node list to return.
        node = video()
        if 'mode' not in self.options:
            self.options['mode']='simple'

        node.options = self.options.copy()
        for key in self.option_spec.keys():
            # fixup paths
            if self.option_spec[key] != docutils.parsers.rst.directives.path:
                continue
            if key not in node.options:
                continue
            node.options[key] = os.path.join(SRC_DIR,node.options[key])

        # check for valid mode
        if node.options['mode'] not in mode_visitors:
            raise ValueError('unknown mode "%s" (should be one of %s)'%(
                node.options['mode'],mode_visitors.keys()))

        # check for .mp4 video file
        if 'video_mp4' not in node.options:
            raise ValueError('video_mp4 option not specified')

        if not os.path.exists(node.options['video_mp4']):
            raise ValueError('video_mp4 "%s" specified, but does not exist (curdir: "%s")'%(
                node.options['video_mp4'], os.path.abspath(os.curdir)))

        # set width, height if not specified
        if not ('width' in node.options and 'height' in node.options):
            # width and/or height not specified

            # read size from video file
            width, height = get_width_height( node.options['video_mp4'] )

            # read specified value if given
            width = node.options.get( 'width', width )
            height = node.options.get( 'height', height )

            # set option
            node.options['width'] = width
            node.options['height'] = height

        if 'video_mp4' in node.options and 'video_ogv' not in node.options:
            ogv_fname = os.path.splitext(node.options['video_mp4'])[0] + '.ogv'
            if os.path.exists(ogv_fname):
                node.options['video_ogv'] = ogv_fname

        node_list = [node]
        return node_list

# from http://camendesign.com/code/video_for_everybody
# downloaded 2010-03-09
video_for_everybody_template_raw = """
<!-- "Video For Everybody" v0.3.2
     =================================================================================================================== -->
<!-- first try HTML5 playback. if serving as XML, expand `controls` to `controls="controls"` and autoplay likewise -->
<video width="640" height="360" poster="__POSTER__.JPG" controls>
	<!-- you must use `</source>` to avoid a closure bug in Firefox 3 / Camino 2! -->
	<source src="__VIDEO__.OGV" type="video/ogg"><!-- Firefox native OGG video --></source>
	<source src="__VIDEO__.MP4" type="video/mp4"><!-- Safari / iPhone video    --></source>
	<!-- IE only QuickTime embed: IE6 is ignored as it does not support `<object>` in `<object>` so we skip QuickTime
	     and go straight to Flash further down. the line break after the `classid` is required due to a bug in IE -->
	<!--[if gt IE 6]>
	<object width="640" height="375" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B"><!
	[endif]-->
	<!-- non-IE QuickTime embed (hidden from IE): the self-closing comment tag allows non-IE browsers to
2	     see the HTML whilst being compatible with serving as XML -->
	<!--[if !IE]><!-->
	<object width="640" height="375" type="video/quicktime" data="__VIDEO__.MP4">
	<!--<![endif]-->
	<param name="src" value="__VIDEO__.MP4" />
	<param name="showlogo" value="false" />
	<param name="autoplay" value="false" />
	<!-- fallback to Flash -->
	<object width="640" height="384" type="application/x-shockwave-flash"
		data="__FLASH__.SWF?image=__POSTER__.JPG&amp;file=__VIDEO__.MP4">
		<!-- Firefox uses the `data` attribute above, IE/Safari uses the param below -->
		<param name="movie" value="__FLASH__.SWF?image=__POSTER__.JPG&amp;file=__VIDEO__.MP4" />
		<!-- fallback image. download links are below the video. warning: putting anything more than
		     the fallback image in the fallback may trigger an iPhone OS3+ bug where the video will not play -->
		<img src="__POSTER__.JPG" width="640" height="360" alt="__Title of video__"
		     title="No video playback capabilities, please download the video below"
		/>
	</object><!--[if gt IE 6]><!-->
	</object><!--<![endif]-->
</video>
<!-- you *must* offer a download link as they may be able to play the file locally. customise this bit all you want -->
<p>Download Video: <a href="__VIDEO__.MP4">Apple iTunes "MP4"</a> | <a href="__VIDEO__.OGV">Open Format "OGG"</a></p>
"""
def _fixup_template(input_template):
    r = input_template
    r = r.replace('640', '%(width)s' )
    r = r.replace('360', '%(height_short)s' )
    r = r.replace('375', '%(height)s' )
    r = r.replace('__POSTER__.JPG', '%(poster_jpg)s' )
    r = r.replace('__FLASH__.SWF', '%(flash_swf)s' )
    r = r.replace('__VIDEO__.MP4', '%(video_mp4)s' )
    r = r.replace('__VIDEO__.OGV', '%(video_ogv)s' )
    r = r.replace('__Title of video__', '%(title)s' )
    return r

video_for_everybody_template = _fixup_template(video_for_everybody_template_raw)

def video_for_everybody_render( node ):
    html = video_for_everybody_template % node.options
    return html

global id_count
id_count = 1

def simple_render( node ):
    global id_count
    v_id = 'video-%d'%id_count
    id_count += 1

    template = '<div %(classes)s>\n'

    atts = []
    browser_controls=False
    if browser_controls:
        atts.append( 'controls' )
    else:
        template += '<div class="docutils-video-controls">\n'
        template += '<input type="button" value="Play" onclick="document.getElementById(\'%(id)s\').play();">'
        template += '<input type="button" value="Pause" onclick="document.getElementById(\'%(id)s\').pause();">'
        template += '</div>\n'

    template += '<div class="docutils-video-player">\n'
    template += '<video width="%(width)s" height="%(height)s" %(atts)s id="%(id)s">\n'
    if 'video_mp4' in node.options:
        template += '  <source src="%(video_mp4)s" type="video/mp4"></source>\n'
    if 'video_ogv' in node.options:
        template += '  <source src="%(video_ogv)s" type="video/ogg"></source>\n'
    template += '</video>\n'
    template += '</div>\n'

    node.setdefault('classes',[]).append('docutils-video-container')
    node.options['classes'] = 'class="' + ' '.join([c for c in node['classes']]) +'"'
    template += '</div>\n'

    node.options['id'] = v_id

    if node.options.get('loop',False):
        atts.append('loop')

    node.options['atts'] = ' '.join(atts)
    html = template % node.options
    return html

mode_visitors = {
    'simple':simple_render,
    'video_for_everybody':video_for_everybody_render,
    }

def visit_video_html(self,node):
    html = mode_visitors[ node.options['mode'] ]( node )
    self.body.append(html)

def depart_video_html(self,node):
    pass


def get_width_height( filename ):
    """get width and height of video using mplayer

    Source: http://www.seiichiro0185.org/doku.php/blog:n900-encode.py_create_n900-friendly_mp4-videos
    """

    import subprocess
    mpdirs = ['/usr/bin','/usr/local/bin']
    for mpdir in mpdirs:
        mpbin = os.path.join(mpdir,'mplayer')
        if os.path.exists(mpbin):
            break
    if not os.path.exists(mpbin):
        raise RuntimeError('no mplayer binary found at %s'%mpbin)

    # Get characteristics using mplayer
    cmd=[mpbin, "-ao", "null", "-vo", "null", "-frames", "0", "-identify", filename]
    mp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    s = re.compile("^ID_VIDEO_ASPECT=(.*)$", re.M)
    m = s.search(mp[0])
    orig_aspect = float(m.group(1))
    s = re.compile("^ID_VIDEO_WIDTH=(.*)$", re.M)
    m = s.search(mp[0])
    orig_width = int(m.group(1))
    s = re.compile("^ID_VIDEO_HEIGHT=(.*)$", re.M)
    m = s.search(mp[0])
    orig_height = int(m.group(1))

    aspect_width = int(round(orig_aspect*orig_height))
    return aspect_width, orig_height

docutils.parsers.rst.directives.register_directive( 'video', VideoDirective )
