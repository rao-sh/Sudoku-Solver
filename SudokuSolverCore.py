import pandas as pd
import numpy as np
import copy
import sys
import time

start_time = time.time()

data = pd.read_csv('SP1.csv', sep=',', header=None)


def count_nans(df):
    '''
    We need to calculate the number of empty boxes in the sudoku grid.
    So, that later we can iterate using it and also determine the progress.
    '''
    counter = 0
    for ind, items in df.iterrows():
        for co, val in enumerate(items):
            if np.isnan(val):
                counter += 1

    return counter


def box_pd(data, r1, r2, c1, c2):
    '''
    We translate the values in the 3x3 grid already provided
     or calculated in the previous iterations colums and rows into a list
    '''
    ib = []
    for items in data.iloc[r1:r2, c1:c2].iteritems():
        for val in items[1]:
            if isinstance(val, int) or val.is_integer():
                if isinstance(val, float):
                    ib.append(int(val))
                else:
                    ib.append(val)

    return ib


def create_inBox_lists(data):
    '''
    We generate a tuple out of 3x3 grids by considering them each at once
    TO-DO: Need to cut down the below maual indexing.
    '''

    # We call box_pd method to generate list of values in grids.
    ib1 = box_pd(data, 0, 3, 0, 3)
    ib2 = box_pd(data, 0, 3, 3, 6)
    ib3 = box_pd(data, 0, 3, 6, 9)
    ib4 = box_pd(data, 3, 6, 0, 3)
    ib5 = box_pd(data, 3, 6, 3, 6)
    ib6 = box_pd(data, 3, 6, 6, 9)
    ib7 = box_pd(data, 6, 9, 0, 3)
    ib8 = box_pd(data, 6, 9, 3, 6)
    ib9 = box_pd(data, 6, 9, 6, 9)

    ibs = (ib1, ib2, ib3, ib4, ib5, ib6, ib7, ib8, ib9)

    return ibs


def create_inRow_lists(data):
    '''
    Here we create a tuple containg lists of all provided or calculted values from each row.
    '''
    irs = ()
    for items in data.iterrows():
        ir = []
        for val in items[1]:
            if not isinstance(val, list):
                if isinstance(val, int) or val.is_integer():
                    if isinstance(val, float):
                        ir.append(int(val))
                    else:
                        ir.append(val)
        irs += (ir,)

    return irs


def create_inCol_lists(data):
    '''
    Here we create a tuple containg lists of all provided or calculted values from each column.
    '''
    ics = ()
    for items in data.iteritems():
        ic = []
        for val in items[1]:
            if not isinstance(val, list):
                if isinstance(val, int) or val.is_integer():
                    if isinstance(val, float):
                        ic.append(int(val))
                    else:
                        ic.append(val)
        ics += (ic,)

    return ics


def find_possibles(df):
    '''
    Here we calculate the possile values for each empty cell in the whole 9x9 grid.
    '''
    inBox_vals = create_inBox_lists(df)
    inRow_vals = create_inRow_lists(df)
    inCol_vals = create_inCol_lists(df)
    master_list = list(range(1, 10))

    for ind, items in df.iterrows():
        # Condition to select 3x3 grids row-wise
        if ind <= 2:
            bi = 0
        elif ind <= 5:
            bi = 3
        else:
            bi = 6

        for co, val in enumerate(items):
            # Conditons to select 3x3 grids column-wise
            if co == 3:
                bi += 1
            elif co == 6:
                bi += 1
            else:
                pass

            if np.isnan(val):
                impossible_values = list(set(inBox_vals[bi]).union(
                    set(inRow_vals[ind])).union(set(inCol_vals[co])))
                possible_values = list(
                    set(master_list) - set(impossible_values))
                if len(possible_values) == 0:
                    sys.exit('''Looks like there is a problem 
                        with the provided values in the question.
                        Please re-check the input.''')
                else:
                    pass
                '''
                TO-DO: This will fill with some positional errors. Still debugging required.
                Probaly a seep up will be results if got to execute this below condition.
                '''
                # elif len(possible_values) == 1:
                #     possible_values = possible_values[0]
                #     print('***Final Value for : (', ind,
                #           ',', co, ') ', possible_values)

                df.loc[ind, co] = possible_values
            else:
                pass
    return df


def colwise_updater(df):
    '''
    Here we consider the lists possible values in each cplumn 
    and update the cells in it if an absolute unique value is possible.
    '''
    ucounter = 0
    for cind, i in df.iteritems():
        mas = []
        for val in i:
            if isinstance(val, list):
                mas.extend(val)
        try:
            nval = [x for x in mas if mas.count(x) == 1][0]
        except Exception as e:
            nval = -1

        if nval != -1:
            rlst = list(df.loc[:, cind].to_dict().values())
            for row_ind, x in enumerate(rlst):
                if isinstance(x, list):
                    for y in x:
                        if y == nval:
                            ''' print('ColWise Updater: Replacing ', df.loc[row_ind, cind], ' with ',
                                nval, ' at (', row_ind, ',', cind, ')') '''
                            df.loc[row_ind, cind] = nval
                            ucounter += 1

    return (df, ucounter)


def rowwise_updater(df):
    '''
    Here we consider the lists possible values in each row 
    and update the cells in it if an absolute unique value is possible.
    '''
    ucounter = 0
    for rind, i in df.iterrows():
        mas = []
        for val in i:
            if isinstance(val, list):
                mas.extend(val)
        try:
            nval = [x for x in mas if mas.count(x) == 1][0]
        except Exception as e:
            nval = -1
        if nval != -1:
            clst = list(df.loc[rind, :].to_dict().values())
            for col_ind, x in enumerate(clst):
                if isinstance(x, list):
                    for y in x:
                        if y == nval:
                            ''' print('RowWise Updater: Replacing ', df.loc[rind, col_ind], ' with ',
                                nval, ' at (', rind, ',', col_ind, ')') '''
                            df.loc[rind, col_ind] = nval
                            ucounter += 1

    return (df, ucounter)


def prev_possibles_nan(df):
    '''
    To assess the possible values again afte col-wise and row-wise updates,
    we set the possible values lists in cells of the 9x9 grid to null.
    '''
    for ind, i in df.iteritems():
        for co, val in enumerate(i):
            if isinstance(val, list):
                df.loc[co, ind] = float('NaN')

    return df


# This enables the dataframe to store data of different type
df = data.astype(object)
nans = count_nans(df)

# To trace progress
prog = []
ucounter = 0


while nans > 0:
    '''
    We need to iterate and update untill no null values are in the 9x9 grid.
    '''
    prog.append(nans)
    dfp = find_possibles(df)

    dfc, c_ucounter = colwise_updater(dfp)

    if c_ucounter != 0:
        dfcn = prev_possibles_nan(dfc)
        dfpc = find_possibles(dfcn)
        dfr, r_ucounter = rowwise_updater(dfpc)

    else:
        dfr, r_ucounter = rowwise_updater(dfc)

    df = prev_possibles_nan(dfr)

    ucounter = c_ucounter + r_ucounter
    nans = count_nans(df)
    prog.append(nans)

    # To validate updates in each iterations
    if prog[-1] == prog[-2]:
        print('''Sorry, The provided question is 
            not truly based on calulations.''')
        print('''It needs Guessing ability, 
            which is still under development.\n\n''')
        print(dfp)
        print('''\n\n**** Use the above results to 
            guess right values manually ****''')
        break
    else:
        pass


if nans == 0:
    print('\nHere is the solution for the question.\n')
    print(df.to_string(header=False, index=False))
else:
    pass


print('\n\t Time taken: ', round((time.time() - start_time), 2), ' seconds\n')
