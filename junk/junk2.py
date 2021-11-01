#! python3

from constants import *

def mytoint(x):
    if type(x) is list: return [mytoint(xi) for xi in x]
    return int(x, 2)

def binary(x, digits=None):
    if type(x) is int:
        res = bin(x)[2:]
    elif type(x) is str:
        res = ''.join(bin(ord(c)).replace('0b','').zfill(8) for c in x) # 8 for utf8

    if digits:
        res = '0' * (digits - len(res)) + res

    return res

def binary_xor(a, b): # one bit character strings
    if a == b: return '0'
    else: return '1'


def binary_and(a, b): # one bit character strings
    if a == '0' or b == '0': return '0'
    else: return '1'

def binary_or(a, b): # one bit character strings
    if a == '0' and b == '0': return '0'
    else: return '1'

def unary_not(a):
    if a == '0': return '1'
    else: return '0'

def generic_bin(binary_fun, *args):
    res = '0' * len(args[0])
    for arg in args:
        res = ''.join(binary_fun(resj, argj) for resj, argj in zip(res, arg))
    return res

def andop(*args):
    res = '1' * len(args[0])
    for arg in args:
        res = ''.join(binary_and(resj, argj) for resj, argj in zip(res, arg))
    return res

xor = lambda *args: generic_bin(binary_xor, *args)
orop = lambda *args: generic_bin(binary_or, *args)
notop = lambda x: ''.join(unary_not(i) for i in x)

# from GFG https://www.geeksforgeeks.org/program-to-add-two-binary-strings/
def binary_adder(x, y):
        max_len = max(len(x), len(y)) 
        x = x.zfill(max_len)
        y = y.zfill(max_len)
        result = ''
        carry = 0
 
        for i in range(max_len - 1, -1, -1):
            r = carry
            r += 1 if x[i] == '1' else 0
            r += 1 if y[i] == '1' else 0
            result = ('1' if r % 2 == 1 else '0') + result
            carry = 0 if r < 2 else 1     
         
        # if carry !=0 : result = '1' + result # commented out intentionally
 
        # return result.zfill(max_len)
        return result

def add(*args):
    res = '0' * len(args[0])
    for arg in args:
        res = binary_adder(res, arg)
    return res

def ror(x, m):
    m = m % len(x)
    x = x[-m:] + x[:-m]
    return x

def lsl(x, m):
    if m > len(x): return '0' * len(x)
    return '0'*m + x[:-m] 


def pad_to_1024_multiple(code):
    width = len(code)
    
    remaining_width = 1024 - width % 1024

    width_of_size_of_original_msg = 128
    tail = binary(width)
    tail = '0' * (width_of_size_of_original_msg - len(tail)) + tail
    remaining_width -= width_of_size_of_original_msg

    padding = '1' + '0' * (remaining_width - 1)

    code = code + padding + tail
    assert (len(code) % 1024 == 0)
    return code


# mixers
rot = lambda x: xor(ror(x, 28), ror(x, 34), ror(x, 39))
rot2 = lambda x: xor(ror(x, 14), ror(x, 18), ror(x, 41))##

def majority (a, b, c):
    return xor(andop(a, b), andop(b, c), andop(c, a)) # xor change to orop

def conditional (a, b, c): 
    return xor(andop(a, b), andop(notop(a), c))

def mixer_one (a, b, c): 
    res = rot(a)
    res = binary_adder(res, majority(a, b, c))
    return res

def mixer_two (wi, ki, e, f, g, h):
    res = conditional(e, f, g)
    res = binary_adder(res, rot2(e))
    res = binary_adder(res, wi)
    res = binary_adder(res, ki)
    res = binary_adder(res, h)
    return res

def mixer_three (wi, ki, a, b, c, d, e, f, g, h):
    m1 = mixer_one(a, b, c)
    m2 = mixer_two(wi, ki, e, f, g, h)
    x = add(m1, m2)
    y = add(d, m2)
    return x, y

word_len = 64

def compression_function(hi, mi):

    assert (len(mi) == 16)
    assert (len(hi) == 8)

    # w needs to contain 80 words
    w = mi

    rotshift_l_m_n = lambda x, l, m, n: xor(ror(x, l), ror(x, m), lsl(x, n))
    rotshift_1_8_7 = lambda x: rotshift_l_m_n(x, 1, 8, 7)
    rotshift_19_61_6 = lambda x: rotshift_l_m_n(x, 19, 61, 6)

    for i in range(16, 80):
        my_tuple_to_add = (
            w[i - 16], 
            rotshift_1_8_7(w[i - 15]),
            w[i - 7],
            rotshift_19_61_6(w[i - 2]),

        )
        w.append(add(*my_tuple_to_add))


    a, b, c, d, e, f, g, h = hi[0], hi[1], hi[2], hi[3], hi[4], hi[5], hi[6], hi[7]

    k = FRACTIONAL_PARTS_OF_CUBES_OF_PRIMES
    k = [binary(ki, digits=64) for ki in k]

    for i in range(80):
        wi = w[i]
        ki = k[i]
        x, y = mixer_three(wi, ki, a, b, c, d, e, f, g, h)
        a, b, c, d, e, f, g, h = x, a, b, c, y, e, f, g

    hi = [a, b, c, d, e, f, g, h]
    return hi

def merkle_damgard(code):
    M = [code[i: i+1024] for i in range(0, len(code), 1024)]
    res = ""
    hi = FRACTIONAL_PARTS_OF_SQRTS_OF_PRIMES
    hi = [binary(hij, digits=64) for hij in hi]
    for mi in M:
        mi = [mi[i: i+64] for i in range(0, len(mi), 64)]
        hi = compression_function(hi, mi)

        resi = ""
        for hij in hi:
            resi += hex(int(hij, 2))[2:]
        print(resi) #f6af ... for "abc"
        res += resi
    return res
    

def pipeline(text):
    code = binary(text)
    # print('length of binary of text =', len(code))
    code = pad_to_1024_multiple(code)
    # print(hex(int(code, 2))[2:])
    # print('length of padded text =', len(code))
    # print('length of padded text divided by 1024 =', len(code) // 1024)
    code = merkle_damgard(code)
    # code = sha_512(code)
    return code


def verify(plain, myhash):
    import hashlib
    # print(hex(plain, 'utf-8'))
    m = hashlib.sha512(bytes(plain, 'utf-8')).hexdigest()
    print("actual", m)
    

def main():
    # plain  =  input('Enter text: ')
    plain = 'abc'
    myhash = pipeline(plain)
    print('Result:', myhash)
    verify(plain, myhash)





main()


















# # I'm going to hell for this
# def full_adder(first, second, carryin):
#     temp = first + second + carryin
#     # truth table for half adder
#     if temp   == '000': s, c = '0', '0'
#     elif temp == '001': s, c = '1', '0'
#     elif temp == '010': s, c = '1', '0'
#     elif temp == '011': s, c = '0', '1'
#     elif temp == '100': s, c = '0', '0'
#     elif temp == '101': s, c = '0', '1'
#     elif temp == '110': s, c = '0', '1'
#     elif temp == '111': s, c = '1', '1'
#     return s, c

# def binary_adder(first, second):
#     carryin = '0'
#     res = ''
#     for a, b in zip(first[::-1], second[::-1]):
#         summ, carryin = full_adder(a, b, carryin)
#         res += summ
#     res = res[::-1]
#     return res