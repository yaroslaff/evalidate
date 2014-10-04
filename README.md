# About Evalidate
Evalidate is simple python module for safe eval()'uating user-supplied (possible malicious) code.

# Examples
    import evalidate

    src="a+b"
    c={'a': 1, 'b': 2}

    success,result = evalidate.safeeval(src,c)
    if success:
        print result
    else:
        print "ERROR:",result
