============================================================================
burst_s5 - standards-compliant HTML slideshows with HTML5 video and Inkscape
============================================================================

`burst_s5`_ is a collection of docutils_ extensions to emit S5_
slideshows (based on `docutils' S5 writer`_) with videos and slides
designed in Inkscape, including appearing elements. It makes S5
presentations a little more like PowerPoint, Keynote, and OpenOffice
Impress.

See a sample presentation `here <http://code.astraw.com/burst_s5/saturn.html>`_.

.. _burst_s5: http://github.com/astraw/burst_s5
.. _docutils: http://docutils.sourceforge.net/
.. _S5: http://meyerweb.com/eric/tools/s5/
.. _docutils' S5 writer: http://docutils.sourceforge.net/docs/user/slide-shows.s5.html

How to use it
=============

A command, *burst2s5* is installed with burst_s5. This takes care of
registering the docutils directives and should otherwise be called
like docutils' own *rst2s5*.

Docutils directives
===================

The following docutils directives are supplied:

video
-----

Emits html5 ``<video>`` tags. Supported:

 * h264 encoded videos in MP4 container files
 * theora encoded videos in Ogg container files
 * both of the above in a single <video> tag

Here is an example of use::

  .. class:: center

    .. video::
     :video_mp4: movie1.mp4
     :height: 400
     :loop: True

This will insert the video ``movie1.mp4`` centered into the
presentation. If the file ``movie1.ogv`` exists alongside the .mp4
file, it will also be inserted. Alternatively, if only the Ogg Video
is available, use the ``:video_ogv:`` option.

inklayers
---------

It allows you to write this in your .rst source file::

  slide title
  -----------

  .. inklayers:: layered_graphics.svg

Instead of manually saving a bunch of layers in Inkscape and then
writing this::

  slide title
  -----------

  .. container:: animation

    .. image:: layer1.png
     :class: hidden slide-display

    .. class:: incremental hidden slide-display

      .. image:: layers12.png

      .. image:: layers123.png

    .. image:: layers1234.png
       :class: incremental

These animated images can be horizontally centered by adding this to
your css::

  /* center the inklayers generated content */
  .inklayers { margin: auto; }

Requirements
============

docutils, lxml.

Inkscape (for the inklayers directive).

On Mac, Inkscape should be installed in /Applications/Inkscape.app. On
others, "inkscape" should be in the path.

Installation
============

This is a standard Python distutils package. Install with::

  python setup.py install

or whatever your usual incantation is. This will put two scripts on
your path: *burst2s5* and *svg-images-abs2rel*.

A sample presentation
=====================

For an example presentation go to ``samples`` and run::

  burst2s5 --theme-url=burst-theme saturn.rst saturn.html

This will generate saturn.html, which illustrates the features of
burst s5.

See the rendered version of this presentation `here
<http://code.astraw.com/burst_s5/saturn.html>`_.

Target screen resolution
========================

The environment variables ``BURST_S5_HEIGHT`` and
``BURST_S5_MAX_WIDTH`` control the resolution of the output.

The "standard" is a 1024x768 screen. These are the defaults. For an
800x600 screen, this seems to work::

  export BURST_S5_MAX_WIDTH="795"
  export BURST_S5_HEIGHT="500"

Also, you may be interested in changing output directory to support
building multiple target resultions simultanously. You can set the
target directory with the ``BURST_S5_INKLAYERS_SUFFIX`` environment
variable.

See also
========

There are other interesting resources about this type of thing:
http://code.google.com/p/html5media/wiki/VideoFormats
