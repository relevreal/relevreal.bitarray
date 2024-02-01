def list_repr(arr):
    arr_str = '['
    i = 0
    for a in arr:
        if i >= 6:
            arr_str += ', ...'
            break
        if i == 0:
            arr_str += str(a)
        else:
            arr_str += f', {a}'
        i += 1
    return arr_str + ']'
