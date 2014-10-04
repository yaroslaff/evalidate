# About Evalidate
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) code.

# Examples
<code>
import evalidate

src="a+b"
c={'a': 1, 'b': 2}

s,r = evalidate.safeeval(src,c)
if s:
    print r
else:
    print "ERROR:",r
</code>