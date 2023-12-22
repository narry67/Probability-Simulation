import sys
import numpy as np
import random
import math
from fitter import Fitter
import matplotlib.pyplot as plt
from statistics import quantiles, mode
np.set_printoptions(threshold=sys.maxsize)

'''PART ONE: FIRST STEP (MARKOV) ANALYSIS'''
total_chips = 10
#Possible coin/chip combinations between two players, the pot, and the turn number (1 or 2)
combinations = []
#Below code assisted by GPT 3.5
# Here we are gathering every combination of states for Markov. p1/p2/pot/turn... person 3 is the pot
for turn in [1,2]:
    for person1_chips in range(total_chips + 1):
        for person2_chips in range(total_chips + 1):
            for person3_chips in range(total_chips + 1):
                if person1_chips + person2_chips + person3_chips == total_chips:
                    combinations.append((person1_chips, person2_chips, person3_chips,turn))
#Above code assisted by GPT 3.5

#End game state
combinations.append(('End Game','End Game', 'End Game', 'End Game'))
#create matrix housing state change probabilities
P = np.zeros((133,133))
#Below, we are assinging probability of going from one state to another in matrix P. combination[i] represents the present state and combination[j] represents the next state.
for i in range(len(combinations)):
    for j in range(len(combinations)):
        #If end game has been reached there can be no more state changes from here
        if combinations[i][0] == 'End Game' and combinations[j][0] == 'End Game':
            P[i,j] = 1
            continue
        #die roll 1: nothing happens. It is the next player's turn so [i][3] and [j][3] must differ
        if combinations[j][0:3] == combinations[i][0:3] and combinations[j][3] != combinations[i][3]:
            P[i,j] += 1 / 6
        ##player 1 turn
        if combinations[i][3] == 1:
            # die roll 2: take the pot. [j][3] must = 2 since j represents the next state and current state is player 1 turn
            if combinations[j][0] == combinations[i][0] + combinations[i][2] and combinations[j][1] == combinations[i][1] \
                and combinations[j][2] == 0 and combinations[j][3] == 2:

                P[i, j] += 1 / 6

            # die roll 3: take half the pot
            if combinations[j][3] == 2 and combinations[j][0] == combinations[i][0] + combinations[i][2] // 2 and \
                combinations[j][1] == combinations[i][1] and combinations[j][2] == combinations[i][2] - combinations[i][2] // 2:

                P[i, j] += 1 / 6

            # die roll 4/5/6: lost one chip to the pot
            if combinations[j][3] == 2 and combinations[j][0] == combinations[i][0]-1 and combinations[j][1] == combinations[i][1] \
                and combinations[j][2] == combinations[i][2]+1:

                P[i, j] += 3 / 6

            #end game: owe a chip to the pot but have none to give. 50% chance of happening if player one is out of chips
            if combinations[i][0] == 0 and combinations[j][0] == 'End Game':

                P[i, j] += 3 / 6

        ##player 2 turn
        elif combinations[i][3] == 2:
            # die roll 2: take the pot
            if combinations[j][1] == combinations[i][1] + combinations[i][2] and combinations[j][0] == combinations[i][0] \
                and combinations[j][2] == 0 and combinations[j][3] == 1:

                P[i, j] += 1 / 6

            # die roll 3: take half the pot
            if combinations[j][3] == 1 and combinations[j][1] == combinations[i][1] + combinations[i][2]//2 \
                and combinations[j][0] == combinations[i][0] and combinations[j][2] == combinations[i][2] - combinations[i][2]//2:

                P[i, j] += 1 / 6

            # die roll 4/5/6: lost one chip to the pot
            if combinations[j][3] == 1 and combinations[j][1] == combinations[i][1] - 1 and combinations[j][0] == \
                combinations[i][0] and combinations[j][2] == combinations[i][2] + 1:

                P[i, j] += 3 / 6
            #end game: owe a chip to the pot but have none to give
            if combinations[i][1] == 0 and combinations[j][0] == 'End Game':

                P[i, j] += 3 / 6




print('Combinations:',combinations)
print('Number of combinations:',len(combinations))
# All rows = 1 indicates that probability of state change is accurate. if a row were greater then that 1 then the probabily of an event occuring would be overestimated
row_sums = np.sum(P, axis=1)
print("Checking that row sums = 1...")
print(row_sums)
#find starting state
index = combinations.index((4,4,2,1))
#create starting state probabilities. 100% chance of starting as problem statement dictates
start = np.zeros(133)
start[index] = 1
#find percent chance of game ending after several different numbers of cycles
#the last row in the matrix represents the end game. Therefore we extract it with [-1]
#a cycle is defined as Player 1 and 2 each completing a turn. Therefore we divide by 2 since we measured total turns
for i in [10,20,30,40,50,60,70,80,90,100]:
    print(f'after {math.ceil(i/2)} cycles', round(start.dot(np.linalg.matrix_power(P,i))[-1]*100,3), 'percent chance of game ending')

print(f'after {math.ceil(26/2)} cycles', round(start.dot(np.linalg.matrix_power(P,26))[-1]*100,3), 'percent chance of game ending')
print(f'after {math.ceil(27/2)} cycles', round(start.dot(np.linalg.matrix_power(P,27))[-1]*100,3), 'percent chance of game ending')


'''PART TWO: ROUGH SIMULATION OF THE GAME'''
#will house each simulation trial
aggregate_rounds = []
#this game function will represent a single run of the game
def game(person1_chips = 4,person2_chips = 4,pot = 2,person1_turn = True,turns = 0):
    #print(f'Player one begins with {person1_chips} chips', f'Player two beings with {person2_chips} chips', f'Pot begins with {pot} chips')
    while person1_chips >= 0 and person2_chips >= 0:
        die_roll = random.randint(1, 6)
        if person1_turn:
            #print(f"Player 1 rolled: {die_roll}")
            if die_roll == 1:
                pass
            elif die_roll == 2:
                person1_chips += pot
                pot = 0
            elif die_roll == 3:
                person1_chips += pot//2
                pot -= pot//2
            else:
                person1_chips -= 1
                pot += 1
            person1_turn = False
        else:
            #print(f"Player 2 rolled: {die_roll}")
            if die_roll == 1:
                pass
            elif die_roll == 2:
                person2_chips += pot
                pot = 0
            elif die_roll == 3:
                person2_chips += pot//2
                pot -= pot//2
            else:
                person2_chips -= 1
                pot +=1
            person1_turn = True
        turns +=1
        #print(f'Player 1 chips: {person1_chips}', f'Player 2 chips: {person2_chips}', f'Pot: {pot}', sep = ' | ')
        if person1_chips < 0:
            #print(f'Player 2 wins in {turns} turns!')
            pass
        if person2_chips < 0:
            #print(f'Player 1 wins in {turns} turns!')
            pass
    #store number of cycles until game ends for every game
    aggregate_rounds.append(math.ceil(turns/2))
#simulate 100000 games
for i in range(100000):
    game()
#print('All rounds:', aggregate_rounds)
print("\nSIMULATION\n")
print(f'Average number of cycles: {sum(aggregate_rounds)/len(aggregate_rounds)}')
q = quantiles(aggregate_rounds)
print(f"The 25, 50, and 75 percentiles are as follows: {q}")
print(f"the mode is {mode(aggregate_rounds)}")
#visualize distribution of each game's cycles with a histogram
bin_edges = np.arange(0, max(aggregate_rounds) + 5, 1) #lines 167-172 assisted with gpt
plt.hist(aggregate_rounds, bins=bin_edges, color='skyblue', edgecolor='black')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram of Data')
plt.show()

#use fitter library to find the distribution that best fits the data
#note that different numbers of simulated games produce different answers here. Creating too large a dataset makes the library time out when fitting the data to many of the distributions.
f = Fitter(aggregate_rounds)
f.fit()
print("Best fitting Distributions...")
print(f.summary())