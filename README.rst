========
burst_s5
========

A collection of utilities docutils extensions to emit S5 slideshows
with videos and slides designed in Inkscape, including appearing
elements. It makes S5 presentations a little more like PowerPoint,
Keynote, and OpenOffice Impress.

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

See also http://code.google.com/p/html5media/wiki/VideoFormats

inklayers
--------

It allows you to write this in your .rst source file::

  responses to natural scenes are contrast independent
  ----------------------------------------------------

  .. inklayers:: layered_graphics.svg

Instead of manually saving a bunch of layers in Inkscape and then
writing this::

  (old) responses to natural scenes are contrast independent
  ----------------------------------------------------------
  							  
  .. container:: animation				  
  							  
    .. image:: layer1.png
     :class: hidden slide-display				  
  							  
    .. class:: incremental hidden slide-display		  
  							  
      .. image:: layers12.png
  							  
      .. image:: layers123.png
  							  
    .. image:: layers1234.png
       :class: incremental				  


Requirements
============

docutils, lxml.

Inkscape (for the inklayers directive).

On Mac, Inkscape should be installed in /Applications/Inkscape.app. On
others, "inkscape" should be in the path.
