=======
plywood
=======

------------
DEMO
------------

::

    load('url')  # basic function call to load in extension
    # parentheses are optional, because things like 'if' and 'for' look
    # better without 'em.  plywood has no "reserved words"
    load 'compress'
    debug = true  # yes, this template language has variable assignment
    a = b = true  # and very limited assignment chaining (no tuples)

    doctype(5)  # or doctype('strict') doctype('xhtml'), etc
    html:  # this'll start looking a lot like jade, but with quotes and colons
      head:
        meta(charset="utf-8")
        title:
          # the if statement, which is a rather complicated plugin because it
          # can be followed by any number of elif's and an optional else.
          if title:
            # docstrings *are* stripped of preceding whitespace (they must be
            # indented), and the first and last newline is removed.
            """
            {title} |
            """  # string interpolation is a little more heavy-duty than
                 # `.format()`, but more similar than different.
          'Welcome'  # string literals require quotes
        compress('css'):
          # notice the function call in here to get the static URL
          link(rel='stylesheet', type='text/css', href=static('css/reset.css'))
          link(rel='stylesheet', type='text/css', href=static('css/welcome.css'))
        script(src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", type="text/javascript")
        compress('js'):
          script(src=static("js/underscore.js"), type="text/javascript")
          script(src=static("js/backbone.js"), type="text/javascript")
        # this outputs the IE conditional, though it looks like an if statement.
        # it's hard to tell the difference between control structures and
        # functions that output (that's because there really *is* no difference)
        ieif 'lt IE 9':
          script(src="//html5shiv.googlecode.com/svn/trunk/html5.js", type="text/javascript")
          link(rel='stylesheet', type='text/css', href=static('css/ie.css'))
        block('extra_head')  # blocks? block inheritance?  of course!
      body:
        div(class="wrapper", id="main-header")  # verbose
        div.wrapper(id="main-header"):  # less verbose

        # I struggled long and hard on what to do about the #id shorthands.
        # in the end, I couldn't in good conscience call this a "python
        # inspired" language if '#' was not the comment delimiter.  So the id
        # shorthand is "@" instead:
        div.wrapper@main-header:  # and yes, that '-' is part of the 'main-header' token!

          # for xml usage, the token parsing will accept some gnarly-looking elements in
          # argument lists:
          book(xmlns='urn:loc.gov:books',
               xmlns:isbn='urn:ISBN:0-395-36341-6'):
               # and elements can be surrounded in '<>' if you so please:
              isbn:number: 1568491379
              <isbn:number>: 1568491379
              # internally, this is called the 'NamespaceOperator'.  The can only
              # appear *within* a VariableToken, not at the beginning or end, and
              # no preceding or trailing whitespace.  It's implemented as an
              # operator because that makes the implementation of unknown elements
              # much easier.
          header:
            block('header'):
              # inlining is easy
              p(class="logo"): 'logo'
              # more complicated inlining
              p: a(href=url("login")): 'Login'
              block('header_title'):
                if user:
                  'Welcome, '{user.name}'
                else:
                  'Welcome'
            if current_member:
              p(class="login"):
                "Welcome, {current_member.preferred_name}"
                a(href=url("logout")): 'Log Out'
          nav:
            ul:
              block('nav'):

          section(class="breadcrumb"):
            block('breadcrumb')

          section(class="main"):
            block('messages'):
              if messages:
                ul(class="messages"):
                  for message in messages:
                    li(class=message.tags):  '{message}'
            script:
              # code literals, so that savvy editors can color the source code
              ```javascript
              $(document).ready(function(){
                $("ul.messages").addClass("animate");

                var fade_out = _(function() {
                  this.addClass("fade-out")
                }).bind($("ul.messages"))

                setTimeout(fade_out, 5000);
                $("ul.messages").bind("click", fade_out);
              });
              ```
            block('content')

          footer:
            # p:
            #   'These are comments.'
            #   span: '|'
            #   '&copy;2012 colinta'

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
you can call ``block.render`` on.  It will be "falsey", though, so you can check
for the existence of a block.  The minimum "truthy" block is an empty string.
That means ``div ''`` will give you a "truthy" block, but ``div`` will be a
"falsey" block.

You can extend the crap out of plywood, because ``div``, ``if``, ``block``, the
whole lot, are all written as plywood extensions.  Without the builtin
extensions, the language couldn't actually *do* anything, because it is at its
core just a language grammar.

-------
WHY!?!?
-------

I think there is room for another templating language.

Haml?  Coffekup?  Jade?  They don't seem pythonic to me.

Plain-Jane HTML?  Sure, if you want.  That is, I think, the best alternative to
plywood.

Even the great django template language is HTML made *nastier* by inserting
*additional markup*.  I looked at Jade and Haml as "yeah, you're getting there",
but they didn't nail it.

I'm unapologettically a DIY-er.  I think that sometimes wheels just need
re-inventing!  Plus, this gave me a chance to play with language grammars, which
I think are fun.  I'm using Modgrammar_

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
