# This is the main signer functions
from Crypto.Util.number import getPrime

def vector_dot_vector(v1, v2):
    assert len(v1)==len(v2)
    sum = 0

    for i in range(len(v1)):
        sum += v1[i]*v2[i]
    
    return sum


def array_row_dot_vector(arr, v):
    result = []
    for i in range(len(arr)):
        result.append(vector_dot_vector(arr[i], v))
    
    return result

def array_column_dot_vector(arr, v):
    result = []
    for i in range(len(arr[0])):
        result.append(vector_dot_vector([arr[j][i] for j in range(len(v))], v))
    
    return result

def gen_keys(key_size=128, row=9, col=3):
    generator = [[getPrime(key_size) for _ in range(row)] for __ in range(col)]
    pub_mask = [getPrime(key_size) for _ in range(col)]
    return {"generator": generator, "pub_mask": pub_mask, "pub_vector": array_column_dot_vector(generator, pub_mask)}


# User verifiable random result, the two outcomes are the same
'''
>>> trial = gen_keys()
>>> vector_dot_vector(trial['pub_vector'], [1337, 202, 120])
366940390711782888758921634675310364294559854809235523912285176836980947721051312
>>> vector_dot_vector(array_column_dot_vector(trial['generator'], [1337, 202, 120]), trial['pub_mask'])
366940390711782888758921634675310364294559854809235523912285176836980947721051312
'''