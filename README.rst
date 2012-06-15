=======
plywood
=======

```
load('url')
load('compress')
doctype('html')  # only accepts literals.  use html5 please.
html:
  head:
    meta(charset="utf-8")
    meta(name="viewport", content="width=device-width; initial-scale=1.0")
    title:
      if title:
        # docstrings *are* stripped of preceding whitespace (they must be
        # indented), and the first and last newline is removed.
        """
        {title} |
        """  # string intepolation is a little more heavy-duty than `.format()`, but more similar than different.
      'Welcome'  # string literals require quotes :-/  I *might* add another way to do this...
    compress('css'):
      link(rel='stylesheet', type='text/css', href=static('css/reset.css'))
      link(rel='stylesheet', type='text/css', href=static('css/welcome.css'))
    script(src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", type="text/javascript")
    compress('js'):
      script(src=static("js/underscore.js"), type="text/javascript")
      script(src=static("js/backbone.js"), type="text/javascript")
    ieif 'lt IE 9':
      script(src="//html5shiv.googlecode.com/svn/trunk/html5.js", type="text/javascript")
      link(rel='stylesheet', type='text/css', href=static('css/ie.css'))
    block('extra_head')  # blocks, and block inheritance?  of course!
  body:
    div(class="wrapper", id="wrapper")  # no shorthand for class and id (yet)
      header:
        block('header'):
          p(class="logo"):
          block('header_title'):
            if user:
              'Welcome, '{user.name}'
            else:
              'Welcome'
        if current_member:
          p(class="login"):
            "Welcome, {current_member.preferred_name}"
            a(href=url("logout")): 'Log Out'
      </header>
      nav:
        ul:
          block('nav'):
            li: a(href=url("login")): 'Login'

      section class="breadcrumb":
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
        #   '&copy;2012 CrossFit'
```

------------
INSTALLATION
------------

::

    $ pip install plywood
    $ ply < in.ply > out.html


-------
LICENSE
-------

:Author: Colin Thomas-Arnold
:Copyright: 2012 Colin Thomas-Arnold <http://colinta.com/>

Copyright (c) 2012, Colin Thomas-Arnold
All rights reserved.

See LICENSE_ for more details (it's a simplified BSD license).
