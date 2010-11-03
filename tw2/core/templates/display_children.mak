<%
attr_keys = w.attrs.keys()
if 'id' in attr_keys:
    attr_keys.remove('id')
if 'class' in attr_keys:
    attr_keys.remove('class')
%>

<%namespace name="tw" module="tw2.core.mako_util"/>\
<div ${tw.attrs(attrs=w.attrs)}>
    % for c in w.children:
     ${c.display() | n}
    % endfor
</div>
