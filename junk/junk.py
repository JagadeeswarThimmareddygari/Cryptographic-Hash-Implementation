
        if i == 23: 
            temp = (
                w[i - 16], 
                rotshift_1_8_7(w[i - 15]),
                w[i - 7],
                rotshift_19_61_6(w[i - 2]),

                )
            
            # print("%%", int(temp[0], 2))
            # print("%%", int(temp[1], 2))
            # print("%%", int(temp[2], 2))
            # print("%%", int(add(
            # w[i - 16], 
            # rotshift_1_8_7(w[i - 15]),
            # w[i - 7],
            # rotshift_19_61_6(w[i - 2]),

            # ),2))
            x, l, m, n = w[i-2], 19, 61, 6
            print("[[",int(x, 2))
            print(int(ror(x, l), 2))
            print(int(ror(x, m), 2))
            print(int(lsl(x, n), 2))


# def string_of_bits_to_bytes(string):
#     b = ''
#     for x in range(0, len(string), 8):
#         each8bits = string[x: x+8]
#         print(each8bits)
#         a = int(each8bits, 2) 
#         print(a)
#         b += chr(a)
#     c = bytes(b, 'ascii')
#     return c

# def string_of_hexs_to_bytes(string):
#     b = ''
#     for x in range(0, len(string), 2):
#         each2hexs = string[x: x+2]
#         print(each2hexs)
#         a = int(each2hexs, 16) 
#         print(a)
#         b += chr(a)
#     print(repr(b))
#     c = bytes(b, 'ascii')
#     return c


# halfbytes = ['0100', '0001', '0100', '0001']
# word = ''.join(halfbytes)
# print(string_of_bits_to_bytes(word))

# word = 'af'
# print(string_of_hexs_to_bytes(word))