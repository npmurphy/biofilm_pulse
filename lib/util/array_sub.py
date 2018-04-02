from numpy import ma
import numpy as np

# this was writting to avoid memory problems on an old laptop. 
# Probably thats not a problem any more and we should not be casting to ints ...
def array_sub(oa, n):
    n = int(n)
    a = oa.copy()
    if ma.isMaskedArray(a):
        proc = np.where((a < n)  & (a.mask==False))
        a[proc] = n
        a = ma.subtract(a, n)
    else:
        a[a < n] = n
        a -= n
    return a