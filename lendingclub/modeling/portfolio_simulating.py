import numpy as np
from numba import jit

@jit
def make_loan_array(l_type, funded, pmt, month, cfs, rem_princp_array, end_m=None):
    '''
    it takes 5 months to go from nonpaying to charged_off (90 days late, 120 default, 150 charged off)
    3 l_types:
    A) default immediately, take 5 months
    B) Fully Prepay between 6-12 months. 
    C) Fully Prepay/pay between 24-36 months
    month: what month the loan was invested in (starts at 0 aka 0 indexed)
    end_m is what month the loan willl end relative to month.
    '''
    # if theoretic:
    #     add_m = np.random.choice(np.arange(-3,4))
    #     if l_type == 'A':
    #         add_cfs = np.zeros(1)
    #     else:
    #         if l_type == 'B':
    #             n_m = 9+add_m+1
    #             print(n_m)
    #         elif l_type == 'C':
    #             n_m = 33+add_m+1
    #         per = np.arange(n_m) + 1
    #         add_cfs = np.tile(pmt, (n_m+1))
    #         rem_princp = (1 - np.ppmt(rate, per, term, funded, 0).sum()).round(2)
    #         add_cfs[-1] += rem_princp
    #     add_cfs[0] = funded
    #     cfs[month:month+len(add_cfs)] += add_cfs
    #     return cfs
    # else:
    assert end_m is not None, "Pass the months on books/months recorded as end_m"
    # Only 2 l_types 'A' default and 'B' (pre)paid, use end_m
    if l_type == 'charged_off':
        n_m = end_m
        add_cfs = np.array([pmt] * int(n_m - 4))
    elif l_type == 'paid':
        n_m = end_m
        add_cfs = np.array([pmt] * int(n_m+1))
        rem_princp = -funded - rem_princp_array[:end_m].sum()
        add_cfs[-1] += rem_princp
    else:
        print('unrecognized loan type')
    add_cfs[0] = funded
    cfs[month:month+len(add_cfs)] += add_cfs
    return cfs


def sim_portfolio(end_d_by_term_stat_grade, sel_loans, ppmt_by_term_rate, n_months=120, n_inv_loans=2000, cfs=None, funded=-1, 
                  verbose=False, longest_winddown=76, wait_for_cont=False):
    '''
    Simulate a portfolio for INVESTING for n_months. Actual portfolio winddown
    may take up to 36 months from last investment date
    funded is the loan amount that will be used (e.g. -1 is one dollar funded to loan)
    Args:
        end_d_by_term_stat_grade: dict pickled from 11_portfolio_simulating.ipynb \
        keys are (term, l_stat, grade) and value = tuple(end_m, probability)
        sel_loans: loans that you can possibly invest in. Samples from this for (term,l_stat, grade)
        funded: should be negative
    '''
    # limit it to relevant columns
    sel_loans = sel_loans[['loan_status', 'grade', 'term', 'int_rate']]
    
    cfs = np.zeros(n_months + longest_winddown) if cfs is None else cfs
    end_i = 0
    for month in range(n_months):
        # end_i keeps track of when you have enough money to reinvest
        if month == end_i:
            if verbose:
                print('month is {0} *************************'.format(month))
            # iterate over loans and construct the cfs array
            n_inv_loans = int(np.floor(n_inv_loans))
            starting_money = abs(n_inv_loans*funded)
            #loans = sel_loans.sample(n=n_inv_loans, replace=True, )
            #li_tups = [tuple(x) for x in loans[['term', 'loan_status', 'grade', 'int_rate']].values]
            #li_tups = [((l.term, l.loan_status, l.grade), l.int_rate) for l in loans.itertuples()]
            loans = sel_loans.sample(n=n_inv_loans, replace=True, ).to_dict('records')
            li_tups = [((l['term'], l['loan_status'], l['grade']), l['int_rate']) for l in loans]
            for l in li_tups:
                # pick the end_m
                #key, rate = l[:3], l[3]
                key, rate = l
                ms, probs = end_d_by_term_stat_grade[key]
                end_m = int(np.random.choice(ms, replace=True, p=probs))
                # key is term, stat, grade
                term, stat, grade = key
                pmt = np.pmt(rate/12, term, funded, 0)
                cfs = make_loan_array(stat, funded, pmt, month, cfs, ppmt_by_term_rate[term, str(round(rate, 4))], end_m=end_m)
                if verbose:
                    print('picking a loan with term: {0}, status: {1}, grade: {2}, and rate: {3}'.format(*key, rate))
                    print('loan life is {0} ending in month {1}'.format(end_m, end_m+month))
                    if wait_for_cont:
                        import ipdb; ipdb.set_trace()
            if verbose:
                print('invested in {0} loans this month'.format(n_inv_loans))
                print('current cfs: {0}'.format(cfs))
                print('current IRR: {0}'.format(np.irr(cfs)*12))
                print('current unadjusted net money: {0}'.format(np.sum(cfs)))
            # calculate which month can reinvest next in
            leftover_money = starting_money - (n_inv_loans * abs(funded))
            assert leftover_money >= 0, 'somehow negative leftover money'
            end_i = month+1
            while (leftover_money < abs(funded)) and (end_i < len(cfs)):
                leftover_money += cfs[end_i]
                end_i += 1
            n_inv_loans = abs(leftover_money/funded)
    # returns the cfs, the net money made, and the annualized irr
    return cfs, np.sum(cfs), np.irr(cfs)*12
