<%namespace name="tw" module="tw2.core.mako_util"/>\
<html>
<head><title>${w.title or ''}</title></head>
<body ${tw.attrs(attrs=w.attrs)}><h1>${w.title or ''}</h1>\
% if w.child:
${w.child.display() | n}\
%endif
</body>
</html>