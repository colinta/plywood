# coding: utf8
from plywood.env import PlywoodEnv


@PlywoodEnv.register_fn()
def reverse(contents):
    return contents[::-1]


@PlywoodEnv.register_fn()
def cdata(contents):
    return '<![CDATA[' + unicode(contents) + ']]>'


@PlywoodEnv.register_fn('len')
def _len(things):
    return len(things)


HTML_ESCAPE_TABLE = {
    u"\"": "&quot;", u"'": "&#039;", u"<": "&lt;", u">": "&gt;", u"¡": "&iexcl;", u"¢": "&cent;", u"£": "&pound;", u"¤": "&curren;", u"¥": "&yen;", u"¦": "&brvbar;", u"§": "&sect;", u"¨": "&uml;", u"©": "&copy;", u"ª": "&ordf;", u"«": "&laquo;", u"¬": "&not;", u"®": "&reg;", u"¯": "&macr;", u"°": "&deg;", u"±": "&plusmn;", u"²": "&sup2;", u"³": "&sup3;", u"´": "&acute;", u"µ": "&micro;", u"¶": "&para;", u"·": "&middot;", u"¸": "&cedil;", u"¹": "&sup1;", u"º": "&ordm;", u"»": "&raquo;", u"¼": "&frac14;", u"½": "&frac12;", u"¾": "&frac34;", u"¿": "&iquest;", u"À": "&Agrave;", u"Á": "&Aacute;", u"Â": "&Acirc;", u"Ã": "&Atilde;", u"Ä": "&Auml;", u"Å": "&Aring;", u"Æ": "&AElig;", u"Ç": "&Ccedil;", u"È": "&Egrave;", u"É": "&Eacute;", u"Ê": "&Ecirc;", u"Ë": "&Euml;", u"Ì": "&Igrave;", u"Í": "&Iacute;", u"Î": "&Icirc;", u"Ï": "&Iuml;", u"Ð": "&ETH;", u"Ñ": "&Ntilde;", u"Ò": "&Ograve;", u"Ó": "&Oacute;", u"Ô": "&Ocirc;", u"Õ": "&Otilde;", u"Ö": "&Ouml;", u"×": "&times;", u"Ø": "&Oslash;", u"Ù": "&Ugrave;", u"Ú": "&Uacute;", u"Û": "&Ucirc;", u"Ü": "&Uuml;", u"Ý": "&Yacute;", u"Þ": "&THORN;", u"ß": "&szlig;", u"à": "&agrave;", u"á": "&aacute;", u"â": "&acirc;", u"ã": "&atilde;", u"ä": "&auml;", u"å": "&aring;", u"æ": "&aelig;", u"ç": "&ccedil;", u"è": "&egrave;", u"é": "&eacute;", u"ê": "&ecirc;", u"ë": "&euml;", u"ì": "&igrave;", u"í": "&iacute;", u"î": "&icirc;", u"ï": "&iuml;", u"ð": "&eth;", u"ñ": "&ntilde;", u"ò": "&ograve;", u"ó": "&oacute;", u"ô": "&ocirc;", u"õ": "&otilde;", u"ö": "&ouml;", u"÷": "&divide;", u"ø": "&oslash;", u"ù": "&ugrave;", u"ú": "&uacute;", u"û": "&ucirc;", u"ü": "&uuml;", u"ý": "&yacute;", u"þ": "&thorn;", u"ÿ": "&yuml;", u"Œ": "&OElig;", u"œ": "&oelig;", u"Š": "&Scaron;", u"š": "&scaron;", u"Ÿ": "&Yuml;", u"ƒ": "&fnof;", u"ˆ": "&circ;", u"˜": "&tilde;", u"Α": "&Alpha;", u"Β": "&Beta;", u"Γ": "&Gamma;", u"Δ": "&Delta;", u"Ε": "&Epsilon;", u"Ζ": "&Zeta;", u"Η": "&Eta;", u"Θ": "&Theta;", u"Ι": "&Iota;", u"Κ": "&Kappa;", u"Λ": "&Lambda;", u"Μ": "&Mu;", u"Ν": "&Nu;", u"Ξ": "&Xi;", u"Ο": "&Omicron;", u"Π": "&Pi;", u"Ρ": "&Rho;", u"Σ": "&Sigma;", u"Τ": "&Tau;", u"Υ": "&Upsilon;", u"Φ": "&Phi;", u"Χ": "&Chi;", u"Ψ": "&Psi;", u"Ω": "&Omega;", u"α": "&alpha;", u"β": "&beta;", u"γ": "&gamma;", u"δ": "&delta;", u"ε": "&epsilon;", u"ζ": "&zeta;", u"η": "&eta;", u"θ": "&theta;", u"ι": "&iota;", u"κ": "&kappa;", u"λ": "&lambda;", u"μ": "&mu;", u"ν": "&nu;", u"ξ": "&xi;", u"ο": "&omicron;", u"π": "&pi;", u"ρ": "&rho;", u"ς": "&sigmaf;", u"σ": "&sigma;", u"τ": "&tau;", u"υ": "&upsilon;", u"φ": "&phi;", u"χ": "&chi;", u"ψ": "&psi;", u"ω": "&omega;", u"ϑ": "&thetasym;", u"ϒ": "&upsih;", u"ϖ": "&piv;", u"–": "&ndash;", u"—": "&mdash;", u"‘": "&lsquo;", u"’": "&rsquo;", u"‚": "&sbquo;", u"“": "&ldquo;", u"”": "&rdquo;", u"„": "&bdquo;", u"†": "&dagger;", u"‡": "&Dagger;", u"•": "&bull;", u"…": "&hellip;", u"‰": "&permil;", u"′": "&prime;", u"″": "&Prime;", u"‹": "&lsaquo;", u"›": "&rsaquo;", u"‾": "&oline;", u"⁄": "&frasl;", u"€": "&euro;", u"ℑ": "&image;", u"℘": "&weierp;", u"ℜ": "&real;", u"™": "&trade;", u"ℵ": "&alefsym;", u"←": "&larr;", u"↑": "&uarr;", u"→": "&rarr;", u"↓": "&darr;", u"↔": "&harr;", u"↵": "&crarr;", u"⇐": "&lArr;", u"⇑": "&uArr;", u"⇒": "&rArr;", u"⇓": "&dArr;", u"⇔": "&hArr;", u"∀": "&forall;", u"∂": "&part;", u"∃": "&exist;", u"∅": "&empty;", u"∇": "&nabla;", u"∈": "&isin;", u"∉": "&notin;", u"∋": "&ni;", u"∏": "&prod;", u"∑": "&sum;", u"−": "&minus;", u"∗": "&lowast;", u"√": "&radic;", u"∝": "&prop;", u"∞": "&infin;", u"∠": "&ang;", u"∧": "&and;", u"∨": "&or;", u"∩": "&cap;", u"∪": "&cup;", u"∫": "&int;", u"∴": "&there4;", u"∼": "&sim;", u"≅": "&cong;", u"≈": "&asymp;", u"≠": "&ne;", u"≡": "&equiv;", u"≤": "&le;", u"≥": "&ge;", u"⊂": "&sub;", u"⊃": "&sup;", u"⊄": "&nsub;", u"⊆": "&sube;", u"⊇": "&supe;", u"⊕": "&oplus;", u"⊗": "&otimes;", u"⊥": "&perp;", u"⋅": "&sdot;", u"⌈": "&lceil;", u"⌉": "&rceil;", u"⌊": "&lfloor;", u"⌋": "&rfloor;", u"〈": "&lang;", u"〉": "&rang;", u"◊": "&loz;", u"♠": "&spades;", u"♣": "&clubs;", u"♥": "&hearts;", u"♦": "&diams;",
}


@PlywoodEnv.register_fn()
def e(text):
    text = unicode(text)
    text = text.replace('&', '&amp;')
    for k in HTML_ESCAPE_TABLE:
        v = HTML_ESCAPE_TABLE[k]
        text = text.replace(k, v)
    ret = ''
    for i, c in enumerate(text):
        if ord(c) > 127:
            ret += hex(ord(c)).replace('0x', '&#x') + ';'
        else:
            ret += c
    return ret
