cimport numpy as np
import numpy as np

cpdef rem_to_be_paid(double out_prncp,
                     double install,
                     double int_rate):
    cdef double m_rate
    cdef double to_be_paid
    m_rate = int_rate/12
    to_be_paid = 0.0
    k = 0
    while out_prncp > 0:
        k += 1
        out_prncp = (1+m_rate) * out_prncp
        out_prncp -= install
        to_be_paid += install
        # the break was added to figure out what was wrong with infinite while; it was due to installment funded
        # being INCORRECTLY REPORTED by lending club
        if k >= 100:
            print(to_be_paid)
            break
        if out_prncp < 0:
            to_be_paid -= abs(out_prncp)
    return to_be_paid

cpdef np.ndarray[double] apply_rem_to_be_paid(np.ndarray col_out_prncp,
                                              np.ndarray col_install,
                                              np.ndarray col_int_rate):
    assert (col_out_prncp.dtype == np.float32 and col_install.dtype == np.float32 and col_int_rate.dtype == np.float32)
    cdef Py_ssize_t i, n = len(col_out_prncp)
    assert (len(col_out_prncp) == len(col_install) == n)
    cdef np.ndarray[double] res = np.empty(n)
    for i in xrange(n):
        res[i] = rem_to_be_paid(col_out_prncp[i],
                                col_install[i],
                                col_int_rate[i])
    return res
