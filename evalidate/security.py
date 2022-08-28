from . import ValidationException, evalidate

simple_attacks = [
"""
os.system("clear")
""",
"""
__import__('os').system('clear')
""",
"""
__builtins__['eval']("print(1)")
""",
]

boom = """
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            {payload}
        ),{{}}
    )()
)()
"""    

boom_payload = [
    # 2.7:          
    '0,0,0,0,"BOOM",(),(),(),"","",0,""',
    
    # 3.5-3.7:      
    '0,0,0,0,0,b"BOOM",(),(),(),"","",0,b""',
    
    # 3.8-3.10:     
    '0,0,0,0,0,0,b"BOOM",(),(),(),"","",0,b""',
    
    # 3.11:         
    '0,0,0,0,0,0,b"BOOM",(),(),(),"","","",0,b"",b"",b"",b"",(),()'

]


def test_attack(attack, safenodes=None, addnodes=None, funcs=None, attrs=None, verbose=False):
    '''
        test attack. return True if attack detected on validation, good. (False if passed, bad)
    '''

    if verbose:
        print("Testing attack code:\n{}".format(attack))

    try:
        node = evalidate(attack, safenodes=safenodes, addnodes=addnodes, funcs=funcs, attrs=attrs)
    except ValidationException as e:
        if verbose:
            print("Good! Attack blocked: {}".format(e))
        return True
    else:
        print("Problem! Attack passed validation without exception!\nCode:\n{}".format(attack))
        return False




def test_security(attacks=None, safenodes=None, addnodes=None, funcs=None, attrs=None, verbose=False):
    ''' 
    test all user-given attacks, or built-in attacks.
    Return value: True if good (all attacks detected), False if at least one attack passes validation
    '''

    # test user-supplied attacks
    if attacks:
        return all( [test_attack(attack=attack, safenodes=safenodes, addnodes=addnodes, funcs=funcs, attrs=attrs, verbose=verbose) for attack in attacks] )


    # test built-in set of attacks
    if not all([test_attack(attack=attack, safenodes=safenodes, addnodes=addnodes, funcs=funcs, attrs=attrs, verbose=verbose) for attack in simple_attacks]):
        return False

    for payload in boom_payload:
        attack = boom.format(payload=payload)
        if not test_attack(attack=attack, safenodes=safenodes, addnodes=addnodes, funcs=funcs, attrs=attrs, verbose=verbose):
            return False
        

    return True