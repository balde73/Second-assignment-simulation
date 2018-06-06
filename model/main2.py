from __future__ import division
import numpy as np
import os

N_NODES = 10

def createStates():
    # Generate the Markov Chain
    states = [] # [n nodes trasmitting:int, m nodes holding:int, no collision:bool]

    for i in range(0, N_NODES+1):
        if i == 0:
            # first state
            states.append([0, 0, True])
        elif i == 1:
            # one node trasmitting. no collision
            for j in range(0, N_NODES+1):
                states.append([1, j, True])
        else:
            # always a collision
            for j in range(0, N_NODES+1):
                states.append([i, j, False])
    print(states)
    return states

def find_state(state, states):
    """
    Return the position in the matrix states of a state
    """
    if state in states:
        return states.index(state)
    else:
        return -1

def computeStartTransmission(item, rate):
    """
    Compute the transition rate
    when a new packet is generated
    """
    return rate * N_NODES

def computeEndTransmission(item, rate):
    """
    Compute the transmission time
    """
    # 10.000 byte with speed 1MB/s
    #if((item[1] * size) < rate):
        #print(rate, " - ", item, " -> ", (rate*size / (rate - (item[1] * size))) )
        #return rate*size / (rate - (item[1] * size))
    return 100

def computeMatrix(states, rate):
    """
    Generate the infinitesimal generator
    """
    matrix = np.zeros((len(states), len(states)))

    for index, item in enumerate(states):
        if item == [0, 0, True]:
            # FIRST STATE can only generate a transmission
            matrix[0][1] = computeStartTransmission([0, 0], rate)
        else:
            # START OF TRANSMISSION
            next_state = [item[0], item[1] + 1, item[2]]
            position = find_state(next_state, states)
            if position != -1:
                matrix[index][position] = computeStartTransmission(item, rate)

            # END OF TRANSMISSION
            status = True if item[1] <= 1 else False
            prev_state = [item[1], 0, status]
            position = find_state(prev_state, states)
            if position != -1:
                matrix[index][position] = computeEndTransmission(item, rate)

    for x in range(0, len(matrix)):
        # fill the diagonal
        matrix[x][x] = -sum(matrix[x])

    return matrix

def append_results(l, steady_state):
    """
    Save the steady state distribution to a csv file
    """
    output = './model/data/output.csv'
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, 'a') as f:
        for index, p in enumerate(steady_state):
            if(index != 0):
                state = states[index]
                val = 't' if state[2] else 'c'
                if p < 0:
                    p = 0
                transmitting = state[0]
                holding = state[1]
                f.write('{},{},{},{},{}\n'.format(transmitting, holding, val, p, l)) 

def replace_last_column_with_1(matrix):
    matrix[::,-1] = 1
    return matrix

if __name__ == "__main__":
    # generate the states of the Markov Chain
    states = createStates()
    N = len(states)

    # open the csv file
    output = './model/data/output.csv'
    f = open(output, 'w+')
    f.write('transmitting,holding,state,prob,rate\n')
    f.close()

    # compute steady state distribution for each possible value of rates
    rates = [500, 400, 300, 250, 200, 175, 150, 125, 100, 75, 50, 45, 40, 38, 35, 32.5, 30, 27.5, 25, 23.5, 22, 19, 17, 15, 13, 12, 11, 10, 9, 8, 7, 6, 5, 2, 1, 0.5, 0.01]
    for rate in rates:
        
        # create the infinitesimal generator
        transition_matrix = computeMatrix(states, rate)
        Q = np.ones((N, N + 1))
        Q[:,:-1] = transition_matrix

        b = [0] * N # a list of zeros
        b.append(1)
        # compute the steady state of the MC
        # use lstsq numpy function to solve ax=b, where a is Q transposed, b is a probability vector like [0,0,...,0,1], x is the returned solution
        # solving the equation 4 in the report
        # https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.lstsq.html
        steady_state_matrix = np.linalg.lstsq(Q.transpose(), b)[0]

        PIQ = np.dot(steady_state_matrix, transition_matrix) # Should be close to zero to prove our result
        error_matrix = np.isclose(a=PIQ, b=np.zeros((N, N)))
        print('[ STEP ] {}, {}'.format(rate, np.all(error_matrix)))

        append_results(rate, steady_state_matrix)
print('Now it is possible to analyze the model in R, just set to TRUE the model part')
