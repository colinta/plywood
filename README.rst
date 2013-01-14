=======
plywood
=======

----
DEMO
----

::

    import url
    from plywood.plugin import compress
    # looks like python so far!
    debug = True  # yes, this template language has variable assignment
    a = b = True  # and limited assignment chaining (no tuples)

    doctype(5)  # or doctype('strict') doctype('xhtml'), etc
    html:  # this'll start looking a lot like jade, but with quotes and colons
      # even though 'html' is a function call, the  parentheses are optional,
      # Things like 'if' and 'for' look better without 'em.  plywood has
      # no "reserved words" - all the language constructs are implemented as
      # plugins.
      head:
        meta(charset="utf-8")
        title:
          # the if statement, which is a rather complicated plugin because it
          # can be followed by any number of elif's and an optional else.
          if self.title:
            # notice the 'self' prefix?  When you pass variables to plywood,
            # they get attached to the 'self' object, to differentiate between
            # plugins and context variables.  You can register globals, too,
            # like the request object.

            # docstrings are stripped of preceding whitespace and the first and
            # last newline is removed.
            """
            {self.title} |
            """  # string interpolation is a little more heavy-duty than
                 # `.format()`, but more similar than different.
          'Welcome'  # string literals require quotes
        compress('css'):
          # passing values to tag attributes are escaped (entitized) automatically
          link(rel='stylesheet', type='text/css', href=url.static('css/reset.css'))
          link(rel='stylesheet', type='text/css', href=url.static('css/welcome.css'))
        script(src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", type="text/javascript")
        compress('js'):
          script(src=url.static("js/underscore.js"), type="text/javascript")
          script(src=url.static("js/backbone.js"), type="text/javascript")
        # this outputs the IE conditional, though it looks like an if statement.
        # it's hard to tell the difference between control structures and
        # functions that output (that's because there really *is* no difference)
        ieif 'lt IE 9':
          script(src="//html5shiv.googlecode.com/svn/trunk/html5.js", type="text/javascript")
          link(rel='stylesheet', type='text/css', href=url.static('css/ie.css'))
        block('extra_head')  # blocks? block inheritance?  of course!
      body:
        div(class="wrapper", id="main-header")  # verbose
        div.wrapper(id="main-header"):  # less verbose

        # I struggled long and hard on what to do about the #id shorthands.
        # in the end, I couldn't in good conscience call this a "python
        # inspired" language if '#' was not the comment delimiter.  So the id
        # shorthand is "@" instead:
        div.wrapper@main-header:  # and yes, that '-' is part of the
             # 'main-header' token.  to support xml/html tag and attribute name,
             # I had to allow ':' and '-' in variable name.

          # for xml usage, the token parsing will accept some gnarly-looking elements in
          # argument lists:
          book(xmlns='urn:loc.gov:books',
               xmlns:isbn='urn:ISBN:0-395-36341-6'):
              isbn:number: 1568491379
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


------
SYNTAX
------

Each line starts with a statement, which can either be a function
(``div``, ``block``) a literal (``'``, ``'''``), or a control statement (``if``,
``else``, ``for``).

Functions get called with the arguments and a "block"::

    # arguments are ((), {}), block is Block()
    p
    # arguments are ((), {'class': 'divvy'}), block is Block()
    div(class="divvy")
    # arguments are (('autofocus'), {'id': 'bio'}), block is Block(Literal('This is my bio'),)
    textarea("autofocus", id="bio"): 'This is my bio'

Even if there is no "block", you'll get at the least at empty block object that
you can call ``block.get_value()`` on.  It will be "falsey", though, so you can check
for the existence of a block.  The minimum "truthy" block is an empty string.
That means ``div: ''`` will have a "truthy" block, but ``div`` will have a
"falsey" block.

You can extend the crap out of plywood, because ``div``, ``if``, ``block``, the
whole lot, are all written as plywood extensions.  Without the builtin
extensions, the language couldn't actually *do* anything, because it is at its
core just a language grammar.

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

:Author: Colin Thomas-Arnold
:Copyright: 2012 Colin Thomas-Arnold <http://colinta.com/>

Copyright (c) 2012, Colin Thomas-Arnold
All rights reserved.

See LICENSE_ for more details (it's a simplified BSD license).

.. _LICENSE:      https://github.com/colinta/StrangeCase/blob/master/LICENSE
.. _Modgrammar:   http://pypi.python.org/pypi/modgrammar
