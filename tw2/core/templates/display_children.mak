<%namespace name="tw" module="tw2.core.mako_util"/>\
% if w.attrs.keys()[:].remove('id'):
<div ${tw.attrs(attrs=w.attrs)}>
% endif
    % for c in w.children:
     ${c.display() | n}
    % endfor
% if w.attrs.keys()[:].remove('id'):
</div>
% endif
