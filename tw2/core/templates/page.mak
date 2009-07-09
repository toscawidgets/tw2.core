<%namespace name="tw" module="tw2.core.mako_util"/>\
<html>
<head><title>${w.title}</title></head>
<body ${tw.attrs(attrs=w.attrs)}><h1>${w.title}</h1>${(w.child and w.child.display()) | n}</body>
</html>