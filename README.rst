=======
plywood
=======

A python-inspired templating language.

----
DEMO
----

::

    import app.url
    import request
    from plywood.plugin import compress

    doctype(5)  # or doctype('strict') doctype('xhtml'), etc.
    html:  # this'll start looking a lot like jade, but with quotes and colons
      # even though 'html' is a function call, the parentheses are optional.
      head:
        meta(charset="utf-8")
        title:
          if self.title:  # context variables are available on 'self'
            # docstrings are stripped of preceding whitespace and the first and
            # last newline is removed.
            """
            {{self.title}} |
            """  # string interpolation uses plywood in 'inline' mode.  Each line
                 # will be joined with a space.
          'Welcome'  # string literals require quotes
        compress('css'):
          # passing values to tag attributes are escaped (html-entitized) automatically
          # if you want to escape using xml, pass {'format': 'xml'} in your options.
          link(rel='stylesheet', type='text/css', href=url.static('css/reset.css'))
          link(rel='stylesheet', type='text/css', href=url.static('css/welcome.css'))
        script(src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", type="text/javascript")
        compress('js'):
          script(src=url.static("js/underscore.js"), type="text/javascript")
          script(src=url.static("js/backbone.js"), type="text/javascript")
        ieif 'lt IE 9':
          script(src="//html5shiv.googlecode.com/svn/trunk/html5.js", type="text/javascript")
          link(rel='stylesheet', type='text/css', href=url.static('css/ie.css'))
        # blocks? block inheritance?  of course!
        block('extra_head')
      body:
        div(class="wrapper", id="main-header"):
          # for xml usage, the token parsing will accept some gnarly-looking elements in
          # argument lists, and this uses the html-plugin constructor, so that
          # you don't have to create a bunch of plugins for your XML documents.
          # (you still need commas between arguments)
          <book xmlns='urn:loc.gov:books',
               xmlns:isbn='urn:ISBN:0-395-36341-6'>:
              <isbn:number>: 1568491379
          header:
            block('header'):
              # inlining is easy
              p(class="logo"): 'logo'
              # more complicated inlining
              p: a(href=url.reverse("login")): 'Login'
              block('header_title'):
                if self.user:
                  'Welcome, '{self.user.name}'
                else:
                  'Welcome'
            if not self.user:
              p(class="login"):
                a(href=url.reverse("login")): 'Log In'
                a(href=url.reverse("logout")): 'Log Out'
          nav:
            ul:
              block('nav'):

          section(class="breadcrumb"):
            block('breadcrumb')

          section(class="main"):
            block('messages'):
              if messages:
                ul(class="messages"):
                  for message in self.messages:
                    li(class=message.tags):  message
            script:
              # code literals, so that savvy editors can color the source code
              '''javascript
              $(document).ready(function(){
                $("ul.messages").addClass("animate");

                var fade_out = _(function() {
                  this.addClass("fade-out")
                }).bind($("ul.messages"))

                setTimeout(fade_out, 5000);
                $("ul.messages").bind("click", fade_out);
              });
              '''
            block('content')

          footer:
            p:
              '&copy;{now(%Y)} colinta'

------------
INSTALLATION
------------

::

    $ pip install plywood
    $ ply < in.ply > out.html


-------
RUNTIME
-------

When you run a plywood template, a lot of the work is done using plugins, which
are loaded into the global context - the ``PlywoodEnv`` object.  This only needs
to happen once per application - the ``PlywoodEnv`` can be reused by any number
of templates (though it is not thread safe - that will be remedied soon).

When you actually ``run`` a compiled ``Plywood`` object, you can pass in a dict
of values that you want

-------
WHY!?!?
-------

The main reason: I envisioned an HTML templating language that had python-like
syntax, and the options that are out there now (Haml, Coffekup, Jade) don't hit
the mark.

Plain-Jane HTML?  Sure, if you want.  That is, I think, the best alternative to
plywood!  For that, use Jinja2.

The template languages that take an HTML-agnostic view (jinja2, django) is HTML
made *nastier* by inserting *additional markup*.  I looked at Jade and Haml as
"yeah, you're getting there", but they didn't nail it.  Plus, have you tried
writing extensions for those systems?  Ooof.  Nasty stuff.  Writing a plugin
for plywood is much easier, and since you can take some part in the parsing and
runtime process, you can write some pretty hefty plugins!

I'm unapologettically a DIY-er.  I think that sometimes wheels just need
re-inventing!

-------
LICENSE
-------

:Author: Colin T.A. Gray
:Copyright: 2012 Colin T.A. Gray <http://colinta.com/>

Copyright (c) 2012, Colin T.A. Gray
All rights reserved.

See LICENSE_ for more details (it's a simplified BSD license).

.. _LICENSE:      https://github.com/colinta/StrangeCase/blob/master/LICENSE
.. _Modgrammar:   http://pypi.python.org/pypi/modgrammar
