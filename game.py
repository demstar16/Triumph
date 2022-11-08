# -*- coding: utf-8 -*-

# authors:
#     Dempsey Thompson (22988643)
#     Robert Sambo (22697311)

from distutils.ccompiler import new_compiler
import getopt, sys, time, random

from networkx.generators.random_graphs import erdos_renyi_graph
import networkx as nx
import csv
from agents import Agent, Green, Blue, Red, Grey
from pyprobs import Probability
import colorama
from colorama import Fore, Back, Style, init
init(autoreset=True)

'''
Sets  up the verbose option for use.
Is only used for game mode 3 when running simulations.
Can be used by adding '-v' when run the game.

It will show much more information about what is going on...
Handy for debugging
'''
try:
    opts, args = getopt.getopt(sys.argv[1:], "v")
except:
    print(f"{Fore.RED}getopt error")
VERBOSE = False
for opt, arg in opts:
    if opt in ['-v']:
        VERBOSE = True

'''
Asks for all the user inputs needed to play the game
It does this through multiple while loops to catch errors
and not cause the game to exit.
'''
print("Welcome to \n")
print(f'''{Fore.YELLOW}
████████ ██████  ██ ██    ██ ███    ███ ██████  ██   ██ 
   ██    ██   ██ ██ ██    ██ ████  ████ ██   ██ ██   ██ 
   ██    ██████  ██ ██    ██ ██ ████ ██ ██████  ███████ 
   ██    ██   ██ ██ ██    ██ ██  ██  ██ ██      ██   ██ 
   ██    ██   ██ ██  ██████  ██      ██ ██      ██   ██
''')

beginning = str(input("PRESS ENTER TO CONTINUE"))

while(1):
    #how many green nodes? 
    try:
        population_size = int(input("\nHow large would you like the general population to be: "))
        if population_size < 1 or population_size > 1000:
            print(f"\n{Fore.RED}Please choose a reasonable number (0-1000) and Try Again\nPS. you can't have negative people")
            continue
    except ValueError:
        print(f"\n{Fore.RED}Choose an Integer!\nPlease Try Again") 
        continue 
    else:
        break

while(1):
    #How long will it run for
    try:
        days = int(input("\nHow many days will the Election go for: "))
        if days < 0 or days > 200:
            print(f"\n{Fore.RED}C'mon now be somewhat realistic... for the computers sake (0-200)")
            continue
    except ValueError:
        print(f"\n{Fore.RED}Please enter an Integer")
        continue
    else:
        break

while(1):
    allowedNumSpies = population_size / 2
    #How many spies
    try:
        num_spies = int(input("\nHow many spies do the Government have access to: "))
        if num_spies < 0 or num_spies > (allowedNumSpies):
            print(f"\n{Fore.RED}C'mon now... that many spies is unfair! (0-" + str(int(allowedNumSpies)) + ")")
            continue
    except ValueError:
        print(f"\n{Fore.RED}Please enter an Integer")
        continue
    else:
        break

if num_spies > 0:
    while(1):
        # How Likely is it that a spy will betray the Government?
        try:
            betray_prob = float(input("\nHow Likely (as a percentage [0-1]) is a spy to BETRAY the Government: "))
            if betray_prob <= 0 or betray_prob >= 1:
                print(f"\n{Fore.RED}Please select a deciaml BETWEEN 0 and 1: ")
                continue
        except ValueError:
            print(f"\n{Fore.RED}Please enter a decimal between 1 and 0.")
            continue
        else:
            break

print(f"\n{Fore.GREEN}Almost there, I promise :)")

while(1):
    #set the probability of the node connection
    try:
        probability = float(input("\nHow well (as a percentage [0-1]) do people know each other: "))
        if probability <= 0 or probability >= 1:
            print(f"{Fore.RED}\nChoose a decimal number BETWEEN 0 and 1\nPlease Try Again")
            continue
    except ValueError:
        print(f"{Fore.RED}\nChoose a decimal number BETWEEN 0 and 1\nPlease Try Again")
        continue
    else:
        break

while(1):
    #set the gamemode  
    # 1 == User Plays as Resistence / Red
    # 2 == User Plays as Governemnt / Blue
    # 3 == User Doesn't Play, it is a simulation 
    try:
        gamemode = int(input("\nWhat gamemode would you like to play?\n1.) Play in the Red Team\n2.) Play in the Blue Team\n3.) Run a Simulation\nCHOOSE WISELY: "))
        if gamemode > 3 or gamemode < 1:
            print(f"\n{Fore.RED}Please be kind and choose a valid option :)\nPlease Try Again")
            continue
    except ValueError:
        print(f"\n{Fore.RED}Please choose a Number")
        continue
    else:
        break

#GLOBAL VARIABLES
n = population_size
p = probability
g = erdos_renyi_graph(n, p)
gov_response = ""
res_response = ""

#AGENTS
redAg = Red("Red Agent")
blueAg = Blue("Blue Agent")
greenAgents = [0] * n
spies = [0] * num_spies 
#Populate Green Agent array
for i in range(n):
    #0-0.2 -> certain (VOTE) & 0.8-1 -> uncertain (NO VOTE)
    # we want the population to start off in the middle
    greenAgents[i] = Green("Person " + str(i), random.uniform(0.2,0.8), random.choice((True,False)))
#Populate Grey Agent array
for i in range(num_spies):
    spies[i] = Grey("Spy " + str(i))
    spies[i].changeBetrayProb(betray_prob)

'''
Helper function to get the current voting state of the population

Returns: int, int represnting current voters and current non voters
'''
def calcVoters():
    voters = 0
    non_voters = 0
    for i in range(n):
        if greenAgents[i].voteStatus == True:
            voters += 1
        else:
            non_voters += 1
    return voters, non_voters

'''
Prints information to the screen each round/day.
Prints different information depending on the game mode.

Returns nothing
'''
def roundSummary():
    voters = 0
    for i in range(n):
        if greenAgents[i].voteStatus == True:
            voters += 1

    if gamemode == 1:
        print(f"\n>>> Green Population: {Fore.YELLOW}{Style.BRIGHT}{n}")
        print(f">>> People who don't want to vote: {Fore.YELLOW}{Style.BRIGHT}{n-voters}")
        print(f"\n>>> {Fore.BLUE}The Governments{Fore.WHITE} Energy (Out of 100): {Style.BRIGHT}{blueAg.energy}")
    if gamemode == 2:
        print(f"\n>>> Green Population: {Fore.YELLOW}{Style.BRIGHT}{n}")
        print(f">>> People who are keen to vote: {Fore.YELLOW}{Style.BRIGHT}{voters}")
    if gamemode == 3 and VERBOSE == True:
        print(f"\n>>> Green Population: {Fore.YELLOW}{Style.BRIGHT}{n}")
        print(f">>> People who are keen to vote: {Fore.YELLOW}{Style.BRIGHT}{voters}")
        print(f">>> People who don't want to vote: {Fore.YELLOW}{Style.BRIGHT}{n-voters}")

'''
Prints a summary at the end of the game for game mode 1.

Parameters:
    blueExhaust -> boolean that determines whether the government ran out of energy
Returns: nothing
'''
def gamemode1Summary(blueExhaust):
    voters = 0
    for i in range(n):
        if greenAgents[i].voteStatus == True:
            voters += 1

    if blueExhaust:
        print(f"\nThe Government has hit {Fore.RED}Exhaustion...\n {Fore.GREEN}{Style.BRIGHT}Congratulations YOU WIN!!!")
    elif voters >= (n/2):
        print(f"\n{Fore.BLUE}{Style.BRIGHT}The Government {Fore.GREEN}Wins\n{Fore.WHITE}You have failed to impact enough people")
    else:
        print(f"""{Style.BRIGHT}{Fore.GREEN}
\nCONGRATULATIONS!!!
You have won and influenced more than half the population\n
I'll see you at the after party *wink*""")

'''
Prints a summary at the end of the game for game mode 2.

Parameters:
    blueExhaust -> boolean that determines whether the government ran out of energy
Returns: nothing
'''
def gamemode2Summary(blueExhaust):
    voters = 0
    for i in range(n):
        if greenAgents[i].voteStatus == True:
            voters += 1

    if blueExhaust:
        if gamemode == 2:
            print(f"\n{Fore.RED}You have hit Exhaustion... {Fore.RED}{Style.BRIGHT}YOU LOSE!")          
    elif voters <= (n/2):
        print(f"\n{Fore.RED}{Style.BRIGHT}The Resistance Wins\n{Fore.WHITE}You have failed to impact enough people")
    else:
        print(f"""{Style.BRIGHT}{Fore.GREEN}
\nCONGRATULATIONS!!!\n
You have won and influenced more than half the population\n
I'll see you at the after party *wink*""")

'''
Prints a summary at the end of the game for game mode 3.

Parameters:
    start -> float representing time when simulation starts
    end -> float representing time when simulation ends
Returns: nothing
'''
def gamemode3Summary(start, end, blueExhaust):
    voters = 0
    for i in range(n):
        if greenAgents[i].voteStatus == True:
            voters += 1
    
    print(f"\nPolitcal Warfare lasted {end-start} seconds")

    print(f"\nTotal Population: {n}")
    print(f"\n{voters} Voters")
    print(f"{n-voters} Non Voters")
    if voters > (n/2):
        print("\nThe Government Win")
    elif blueExhaust:
        print("\n The Government lost due to Exhaustion")
    else:
        print("\nThe Resistence Win")

'''
Manipulates the data in the graph object into a dictionary where the keys are the 
nodes in the graph and the values are lists containing nodes that the key is 
connected to.

Parameters:
    graphObject -> graph object (from networkx), is a list of tuples representing
                    all the node connections in the Erdos Renyi Graph
Returns: dictionary
'''
def edgeDict(graphObject):
    edgeDict = {}
    for connection in graphObject.edges(data=True):
        if connection[0] not in edgeDict.keys():
            edgeDict[connection[0]] = []

    for i in edgeDict.keys():
        for connection in graphObject.edges(data=True):
            if connection[0] == i:
                edgeDict[i].append(connection[1])

    return edgeDict

'''
Uses the dictioanry of connections to loop through the green network and if there is a connection,
check the uncertainties and if one of the nodes is very certain of their choice they have a 50%
chance of changing the opinion/vote status of the other person.

Parameters: 
    edgeDict -> dictionary of nodes as keys and a array each nodes connections as values 
Returns: nothing
'''
def greenNetworkInteraction(edgeDict):
    for node in edgeDict.items(): #0:[1,2,3,5]
        for connection in range(len(node[1])):
            person1 = greenAgents[node[0]]
            person2 = greenAgents[node[1][connection]]

            if person1.uncertainty < person2.uncertainty and person1.uncertainty < 0.15 and Probability.prob(0.5):
                if person1.voteStatus is not person2.voteStatus and person2.uncertainty < 0.8: 
                    #person2.changeVoteStatus(person1.voteStatus)
                    #Being swayed towards the government... although their vote has changed their uncertainty only changes slightly
                    old_uncertainty = person2.uncertainty
                    new_uncertainty = person2.uncertainty - (person2.uncertainty*0.1)
                    person2.uncertainty = new_uncertainty

                    if gamemode == 3 and VERBOSE == True:
                        print(f"node {person1.name} influenced node {person2.name} uncertainty by: {abs(old_uncertainty-new_uncertainty)}")

            elif person2.uncertainty < person1.uncertainty and person2.uncertainty < 0.15 and Probability.prob(0.5):
                if person2.voteStatus is not person1.voteStatus and person1.uncertainty < 0.8:
                    #person1.changeVoteStatus(person2.voteStatus)
                    #Being swayed towards the government... although their vote has changed their uncertainty only changes slightly
                    old_uncertainty = person1.uncertainty
                    new_uncertainty = person1.uncertainty - (person1.uncertainty*0.1)
                    person1.uncertainty = new_uncertainty
                
                    if gamemode == 3 and VERBOSE == True:
                        print(f"node {person2.name} influenced node {person1.name} uncertainty by: {abs(old_uncertainty-new_uncertainty)}")

            elif person1.uncertainty > person2.uncertainty and person1.uncertainty > 0.85 and Probability.prob(0.5):
                if person1.voteStatus is not person2.voteStatus and person2.uncertainty > 0.2:
                    #person2.changeVoteStatus(person1.voteStatus)
                    #Being swayed towards the government... although their vote has changed their uncertainty only changes slightly
                    old_uncertainty = person2.uncertainty
                    new_uncertainty = person2.uncertainty + (person2.uncertainty*0.1)
                    person2.uncertainty = new_uncertainty

                    if gamemode == 3 and VERBOSE == True:
                        print(f"node {person1.name} influenced node {person2.name} uncertainty by: {abs(old_uncertainty-new_uncertainty)}")

            elif person2.uncertainty > person1.uncertainty and person2.uncertainty > 0.85 and Probability.prob(0.5):
                if person2.voteStatus is not person1.voteStatus and person1.uncertainty > 0.2:
                    #person1.changeVoteStatus(person2.voteStatus)
                    #Being swayed towards the government... although their vote has changed their uncertainty only changes slightly
                    old_uncertainty = person1.uncertainty
                    new_uncertainty = person1.uncertainty + (person1.uncertainty*0.1)
                    person1.uncertainty = new_uncertainty

                    if gamemode == 3 and VERBOSE == True:
                        print(f"node {person2.name} influenced node {person1.name} uncertainty by: {abs(old_uncertainty-new_uncertainty)}")

'''
Checks every nodes uncertainty to see whether or not it is in a range that can determine 
its new vote status or if it has gone of bounds and we then readjust it if it does

Returns: nothing
'''
def greenUcertaintyCheck():
    for i in range(n):
        person = greenAgents[i]
        # person uncertainty has caused them to change their mind
        if person.uncertainty > 0.8:
            person.changeVoteStatus(False) 
        elif 0 < person.uncertainty < 0.2:
            person.changeVoteStatus(True)
        
        # Check to keep uncertainty in bounds
        if person.uncertainty >= 1:
            person.uncertainty = 0.950
        elif person.uncertainty <= 0.05:
            person.uncertainty = 0.050

'''
This function incoorporates the intelligence aspect of the project.
It finds the probability of a message being received well given the uncertainty of an agent.

Parameters:
    baysianProb -> float representing the probability of a agent being uncertain when a msg is received well
    msgProb -> float representing the probability of a message being recevied well
    agentUncertainty -> float representing the uncertainty of an agent
Returns: float representing a probability
'''
def bayesianRule(baysianProb, msgProb, agentUncertainty):
    bayesianProbability = (baysianProb * msgProb)/agentUncertainty

    string = str(bayesianProbability)
    if len(string) > 5:
        return_prob = float(string[:5])
    else:
        return_prob = float(string)

    if return_prob > 1.0:
        return_prob = 0.987
    elif return_prob < 0.0:
        return_prob = 0.012

    return float(return_prob)

'''
Prompts the user with what is needed for game mode 1.
Playing as the Resistence

Returns: nothing
'''
def gamemode1Intro():
    while(1):
        try:
            blueUncertainty = float(input("\nHow uncertain [as a percentage (0-1)] is your opponent, the Government: "))
            if blueUncertainty >= 1 or blueUncertainty <= 0:
                print(f"\n{Fore.RED}Please be kind and choose a valid option :)\nPlease Try Again")
                continue
        except ValueError:
            print(f"\n{Fore.RED}Please choose a Decimal (0-1)")
            continue
        else:
            break
    blueAg.setUncertainty(blueUncertainty)


    redAg.setUncertainty(0.01) #not used but needed


    theResistance = f"""{Fore.RED}{Style.BRIGHT}
████████╗██╗░░██╗███████╗
╚══██╔══╝██║░░██║██╔════╝
░░░██║░░░███████║█████╗░░
░░░██║░░░██╔══██║██╔══╝░░
░░░██║░░░██║░░██║███████╗
░░░╚═╝░░░╚═╝░░╚═╝╚══════╝

██████╗░███████╗░██████╗██╗░██████╗████████╗░█████╗░███╗░░██╗░█████╗░███████╗
██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝██╔══██╗████╗░██║██╔══██╗██╔════╝
██████╔╝█████╗░░╚█████╗░██║╚█████╗░░░░██║░░░███████║██╔██╗██║██║░░╚═╝█████╗░░
██╔══██╗██╔══╝░░░╚═══██╗██║░╚═══██╗░░░██║░░░██╔══██║██║╚████║██║░░██╗██╔══╝░░
██║░░██║███████╗██████╔╝██║██████╔╝░░░██║░░░██║░░██║██║░╚███║╚█████╔╝███████╗
╚═╝░░╚═╝╚══════╝╚═════╝░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝░╚════╝░╚══════╝"""
    summary = f""" {Fore.RED}
█▀ █░█ █▀▄▀█ █▀▄▀█ ▄▀█ █▀█ █▄█
▄█ █▄█ █░▀░█ █░▀░█ █▀█ █▀▄ ░█░"""

    print(f"\nYou are the new leader of......\n" +theResistance)
    input(summary + f"""{Fore.RED}
The Resistance is an anti-political group, determined to lower the influence of the Government. 
They can send out messages convincing the population not to vote.

However, the stronger the message, the higher you are at risk of losing followers. 
If the message is successfully recieved, the more of an impact you will have.

BEWARE, the government can also send out spies that are disguised as a member of The Resistance. 
They can potentially sabotage our plans and cause us to lose followers.
 
You have """ + str(days) + f" days until election day to make as many people not want to vote as possible, Goodluck!\n{Fore.WHITE}(PRESS ENTER)")

'''
Prompts the user with what is needed for game mode 2.
Playing as the Government

Returns: nothing
'''
def gamemode2Intro():

    while(1):
        try:
            redUncertainty = float(input("\nHow uncertain [as a percentage (0-1)] is your opponent, the Resistence: "))
            if redUncertainty >= 1 or redUncertainty <= 0:
                print(f"\n{Fore.RED}Please be kind and choose a valid option :)\nPlease Try Again")
                continue
        except ValueError:
            print(f"\n{Fore.RED}Please choose a Decimal (0-1)")
            continue
        else:
            break
    redAg.setUncertainty(redUncertainty)


    blueAg.setUncertainty(0.01) #not used but needed


    government = f"""{Fore.CYAN}
░██████╗░░█████╗░██╗░░░██╗███████╗██████╗░███╗░░██╗███╗░░░███╗███████╗███╗░░██╗████████╗
██╔════╝░██╔══██╗██║░░░██║██╔════╝██╔══██╗████╗░██║████╗░████║██╔════╝████╗░██║╚══██╔══╝
██║░░██╗░██║░░██║╚██╗░██╔╝█████╗░░██████╔╝██╔██╗██║██╔████╔██║█████╗░░██╔██╗██║░░░██║░░░
██║░░╚██╗██║░░██║░╚████╔╝░██╔══╝░░██╔══██╗██║╚████║██║╚██╔╝██║██╔══╝░░██║╚████║░░░██║░░░
╚██████╔╝╚█████╔╝░░╚██╔╝░░███████╗██║░░██║██║░╚███║██║░╚═╝░██║███████╗██║░╚███║░░░██║░░░
░╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚══╝░░░╚═╝░░░"""
    print("\n\nThere's no messing around when you're working for the.........\n"+government) 
    
    summary = f""" {Fore.CYAN}
    
█▀ █░█ █▀▄▀█ █▀▄▀█ ▄▀█ █▀█ █▄█
▄█ █▄█ █░▀░█ █░▀░█ █▀█ █▀▄ ░█░"""

    input(summary + f"""\n {Fore.CYAN}
The Government is a political group, determined to take full control over the country. 
They have the power to rule the entire population. There only enemy is The Resistance, an anti-political group
who are doing everything in their power to sabotage the Governments operation. You can send messages to convince the masses
to vote. 

However, you have a energy bar (not the food), the stronger the message you send, the more energy you use. Once your energy's
all used up, you LOSE!

You can also send out spies that are disguised as a member of The Resistance. 
They can potentially sabotage their plans and cause them, to lose followers.
 
You have """ + str(days) + f" days until election day to make as many people vote as possible, Goodluck!\n{Fore.WHITE}(PRESS ENTER)")

'''
Prompts the user with extra requirements needed for game mode 3.
Running a Simulation

Returns: nothing
'''
def gamemode3Intro():
    while(1):
        try:
            blueUncertainty = float(input("\nHow uncertain [as a percentage (0-1)] is the Government: "))
            if blueUncertainty >= 1 or blueUncertainty <= 0:
                print(f"\n{Fore.RED}Please be kind and choose a valid option :)\nPlease Try Again")
                continue
        except ValueError:
            print(f"\n{Fore.RED}Please choose a Decimal (0-1)")
            continue
        else:
            break
    blueAg.setUncertainty(blueUncertainty)

    while(1):
        try:
            redUncertainty = float(input("\nHow uncertain [as a percentage (0-1)] is the Resistence: "))
            if redUncertainty >= 1 or redUncertainty <= 0:
                print(f"\n{Fore.RED}Please be kind and choose a valid option :)\nPlease Try Again")
                continue
        except ValueError:
            print(f"\n{Fore.RED}Please choose a Decimal (0-1)")
            continue
        else:
            break
    redAg.setUncertainty(redUncertainty)

'''
Sends a message to the population and effects the uncertainty of everyone individually
depending on the potency of the message and uncertainty of the agent.

Parameters:
    potency -> int: level of potency of the message being sent
    msgProb -> float: probability of message being rreceived well
    baysianProb -> float: probability of an agent being ucnertain given that the message was received well
    agent -> string: agent who sent the message
    greenUncertaintyChange -> float: factor by which to change the uncertainty of a green node
Returns: boolean
'''
def sendMsg(potency, msgProb, baysianProb, agent, greenUncertaintyChange):
    if agent == 'blue':
        probMsgReceivedWell = bayesianRule(baysianProb, msgProb, blueAg.uncertainty)
    elif agent == 'red':
        probMsgReceivedWell = bayesianRule(baysianProb, msgProb, redAg.uncertainty)

    if gamemode == 1 and agent == 'red':
        probMsgReceivedWell = msgProb
    elif gamemode == 2 and agent == 'blue':
        probMsgReceivedWell = msgProb

    before_voters, before_non_voters = calcVoters()

    if gamemode == 3 and VERBOSE == True:
        print(f"Probability of Message being received well: {probMsgReceivedWell}")

    for i in range(n):
        personUncertainty = greenAgents[i].uncertainty
        if Probability.prob(probMsgReceivedWell) == True and agent == 'red':
            #First 2 ifs are to give proper reward for when the uncertainties get really low
            if personUncertainty < 0.15 and potency > 3:
                new_uncertainty = personUncertainty * 5
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")
            elif personUncertainty < 0.15 and potency < 4:
                new_uncertainty = personUncertainty * 2
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")
            else:
                new_uncertainty = personUncertainty + (personUncertainty * greenUncertaintyChange)
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")

        elif Probability.prob(probMsgReceivedWell) == True and agent == 'blue':
            new_uncertainty = personUncertainty - (personUncertainty * greenUncertaintyChange)
            greenAgents[i].uncertainty = new_uncertainty
            if gamemode == 3 and VERBOSE == True:
                print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")

        elif Probability.prob(probMsgReceivedWell) == False and agent == 'red': 
            # Makes the reward less severe for those who are still uncertain... but those who are
            # already certain will not be happy about it
            if personUncertainty < 0.3: #how close to being certian they need to be
                new_uncertainty = personUncertainty - (personUncertainty * greenUncertaintyChange)
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")
            else:
                new_uncertainty = personUncertainty - ((personUncertainty - 0.2) * greenUncertaintyChange)
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")
        else:
            # Makes the reward less severe for those who are still uncertain... but those who are already certain will not be happy about it
            if personUncertainty < 0.15 and potency > 3:
                new_uncertainty = (personUncertainty * 3)
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")
            elif personUncertainty < 0.15 and potency < 4:
                new_uncertainty = (personUncertainty * 2)
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")
            else:
                new_uncertainty = personUncertainty + (personUncertainty * greenUncertaintyChange)
                greenAgents[i].uncertainty = new_uncertainty
                if gamemode == 3 and VERBOSE == True:
                    print(f"\tCOUNTER " + str(potency) + f": node {greenAgents[i].name} uncertainty change: {personUncertainty} --> {new_uncertainty}: {greenAgents[i].voteStatus}")

    greenUcertaintyCheck()

    after_voters, after_non_voters = calcVoters()

    if (after_voters > before_voters and agent == 'blue') or (after_non_voters > before_non_voters and agent == 'red'):
        return True
    else:
        return False


'''
Effects the uncertainty of the agent depending on the results of the message it sent.

Parameters:
    potency -> int: level of potency of the message
    agent -> string: agent who sent the message
    success -> boolean: whether the message was received well or not
    neutral -> boolean: whether the message had no impact or not (in terms of vote status)
Returns: nothing
'''
def agentUncertaintyChange(potency, agent, success, neutral=False):
    #Agent knows it is a risk... success lowers uncertainty more than failure increases it
    if potency == 5:
        if agent == 'red' and success == True:
            redAg.changeUncertainty(-(redAg.uncertainty*0.25))
        elif agent == 'red' and success == False:
            redAg.changeUncertainty(redAg.uncertainty*0.1)
        elif agent == 'blue' and success == True:
            blueAg.changeUncertainty(-(blueAg.uncertainty*0.25))
        else:
            blueAg.changeUncertainty(blueAg.uncertainty*0.1)

    if potency == 4:
        if agent == 'red' and success == True:
            redAg.changeUncertainty(-(redAg.uncertainty*0.175))
        elif agent == 'red' and success == False:
            redAg.changeUncertainty(redAg.uncertainty*0.125)
        elif agent == 'blue' and success == True:
            blueAg.changeUncertainty(-(blueAg.uncertainty*0.155))
        else:
            blueAg.changeUncertainty(blueAg.uncertainty*0.125)

    if potency == 3:
        if agent == 'red' and success == True:
            redAg.changeUncertainty(-(redAg.uncertainty*0.1))
        elif agent == 'red' and success == False:
            redAg.changeUncertainty(redAg.uncertainty*0.1)
        elif agent == 'blue' and success == True:
            blueAg.changeUncertainty(-(blueAg.uncertainty*0.1))
        else:
            blueAg.changeUncertainty(blueAg.uncertainty*0.1)

    #The following 2 aren't "risky"... failure will affect uncertainty more than success
    if potency == 2:
        if agent == 'red' and success == True:
            redAg.changeUncertainty(-(redAg.uncertainty*0.1))
        elif agent == 'red' and success == False:
            redAg.changeUncertainty(redAg.uncertainty*0.125)
        elif agent == 'blue' and success == True:
            blueAg.changeUncertainty(-(blueAg.uncertainty*0.1))
        else:
            blueAg.changeUncertainty(blueAg.uncertainty*0.125)

    if potency == 1:
        if agent == 'red' and success == True:
            redAg.changeUncertainty(-(redAg.uncertainty*0.075))
        elif agent == 'red' and success == False:
            redAg.changeUncertainty(redAg.uncertainty*0.175)
        elif agent == 'blue' and success == True:
            blueAg.changeUncertainty(-(blueAg.uncertainty*0.075))
        else:
            blueAg.changeUncertainty(blueAg.uncertainty*0.175)

    #no effect on the population will slightly increase uncertianty
    if neutral == True:
        if agent == 'red':
            redAg.changeUncertainty(redAg.uncertainty*0.025)
        elif agent == 'blue':
            blueAg.changeUncertainty(blueAg.uncertainty*0.025)

'''
Provides the user interface / game for game mode 1.
Playing as the Resistence.
The choices that the user is prompted with affects the green nodes uncertainties.

Returns: nothing
'''
def redUserGameplay():
    print("Below is a list of actions from 1-5, each with a different level of strength and consequences.\n(1 being the weakest and 5 being the strongest)")
    while(1):
        try:
            chosenMsg = int(input("\nPlease Choose an Action\n1: Anti-Campaign Video\n2: Peaceful Protest\n3: Hand out Flyers\n4: Anti-Campaign Online Petition\n5: Raid the White House\nChoose Cautiously... (or don't, I don't really care): "))
            if chosenMsg < 0 or chosenMsg > 5:
                print(f"{Fore.RED}\nI don't believe that was an option now was it?")
                continue
        except ValueError:
            print(f"{Fore.RED}\n...really?\nPlease choose a number")
            continue
        else:
            break
    
    def antiCampaignVideo():
        sendMsg(1, 0.8, 0, 'red', 0.1)
            
    def peacefulProtest():
        sendMsg(2, 0.65, 0, 'red', 0.2)

    def handOutFlyers():
        sendMsg(3, 0.5, 0, 'red', 0.3)

    def antiCampaignOnlinePetition():
        sendMsg(4, 0.35, 0, 'red', 0.5)

    def raidtheWhiteHouse():
        sendMsg(5, 0.1, 0, 'red', 0.7)
            
    
    while(True):
        if chosenMsg == 1:
            antiCampaignVideo()
            print("\n>>> So you chose an anti-campaign video, playing it safe... I like it")
            break
        elif chosenMsg == 2:
            peacefulProtest()
            print("\n>>> The peaceful protest went... peacefully")
            break
        elif chosenMsg == 3:
            handOutFlyers()
            print("\n>>> Handing out flyers, interesting choice... I like it")
            break
        elif chosenMsg == 4:
            antiCampaignOnlinePetition()
            print("\n>>> Now you're taking some risks! The anti-campaign online petition is live!")
            break
        elif chosenMsg == 5:
            raidtheWhiteHouse()
            print(f"\n>>> You are a mad man, have fun {Fore.RED}RAIDING THE WHITEHOUSE")
            break
        else: 
            print("Please enter valid option.")
            chosenMsg = int(input("1: Anti-Campaign Video\n2: Peaceful Protest\n3: Hand out Flyers\n4: Anti-Campaign Online Petition\n5: Raid the White House\nC'mon! You can do this: "))

'''
Provides the user interface / game for game mode 2.
Playing as the Government.
The choices that the user is prompted with affects the green nodes uncertainties.

Returns: nothing
'''
def blueUserGameplay():
    isSpy = False

    #WARN the user if they are very low on energy
    if (blueAg.usrEnergy < 10):
        print("\n {Fore.RED}YOU ARE EXTREMELY LOW ON ENERGY...\nPROCEED WITH CAUTION")

    #Prompt user with first option
    print(">>> How would you like to proceed sir?")
    while(1):
        try:
            decision = int(input(f"""
1.) Counter Narrative
2.) Send Spy
3.) Skip a Day and get some rest

You have {Style.BRIGHT}{len(spies)}{Style.NORMAL} spies at your disposal
Your energy level is currently at {Style.BRIGHT}{blueAg.usrEnergy}%

Your Choice: """))
            if decision < 1 or decision > 3:
                print(f"{Fore.RED}I don't think that was an option")
                continue
        except ValueError:
            print(f"{Fore.RED}Please enter an Integer")
            continue
        else:
            break
    
    print(f"{Fore.YELLOW}\n-------------------------------------------------------------\n")

    #Message of HIGHEST potency
    def counter5():
        sendMsg(5, 0.1, 0, 'blue', 0.7)
            
    #Message of second HIGHEST potency
    def counter4():
        sendMsg(4, 0.35, 0, 'blue', 0.5)

    #Message of MEDIUM potency
    def counter3():
        sendMsg(3, 0.5, 0, 'blue', 0.3)

    #Message of second LOWEST potency
    def counter2():
        sendMsg(2, 0.7, 0, 'blue', 0.2)

    #Message of LOWEST priority
    def counter1():
        sendMsg(1, 0.9, 0, 'blue', 0.1)

    #Sends a spy
    def sendSpy(index):
        if spies[index].betray == True:
            if gamemode == 1:
                print("\n>>> The Government has sent a Spy... Luckily he is one of ours")
            elif gamemode == 2:
                print("\n>>> Your Spy has betrayed you")
                if Probability.prob(0.1) == True:
                      #Sends a potent message for the Resistence with no consequence
                      new_uncertainty = greenAgents[i].uncertainty + (greenAgents[i].uncertainty * 0.7)
                      greenAgents[i].changeUncertainty(new_uncertainty)
        else:
            if gamemode == 1:
                print("\n>>> The Government broke into our system, we found a Spy")
            elif gamemode == 2:
                print("\n>>> We have successfully infiltrated the Resistence")
            isSpy = True
            return isSpy

    #Set of if statements to prompt the user with the correct second prompt depending on what they chose in the first prompt
    if decision == 1:
        print("Below is a list of actions from 1-5, each with a different level of strength and consequences.\n(1 being the weakest and 5 being the strongest)")
        while(1):
            try:
                chosenMsg = int(input(f"""{Style.BRIGHT}
Please Choose an Action
1: Campaign Video
2: Electoral Event
3: Subliminal Messages
4: Announce Free HealthCare
5: Operation MKULTRA
Choose Cautiously... (or don't, I don't really care): """))

                if chosenMsg < 0 or chosenMsg > 5:
                    print(f"{Fore.CYAN}\nI don't believe that was an option now was it?")
                    continue
            except ValueError:
                print(f"{Fore.CYAN}\n...really?\nPlease choose a number")
                continue
            else:
                break

        #What action the user chose
        if chosenMsg == 1:
            counter1()
            print("\n>>> So you chose an campaign video, playing it safe... I like it")
            if isSpy == False:
                blueAg.useUserEnergy(5)
            else:
                isSpy = False
        elif chosenMsg == 2:
            counter2()
            if isSpy == False:
                blueAg.useUserEnergy(10)
            else:
                isSpy = False
            print("\n>>> Nothing like an old school electoral event!")
        elif chosenMsg == 3:
            counter3()
            if isSpy == False:
                blueAg.useUserEnergy(15)
            else:
                isSpy = False
            print("\n>>> very sneaky! Making the massess 'think for themselves' ")
        elif chosenMsg == 4:
            counter4()
            if isSpy == False:
                blueAg.useUserEnergy(20)
            else:
                isSpy = False
            print("\n>>> Now you're taking some risks! Hopefully it's not like ObamaCare!")
        elif chosenMsg == 5:
            counter5()
            if isSpy == False:
                blueAg.useUserEnergy(25)
            else:
                isSpy = False
            print(f"\n>>> The land of the free......... {Fore.RED}OPERATION MIND CONTROL!")

    elif decision == 2:
    #Send a spy if available
        if len(spies)>0:
            isSpy = sendSpy(0)
            spies.pop()
        else:
            print("\nYou don't have any spies... you just sent nothing \nWhat a waste of a turn );")

    elif decision == 3:
    #restore some energy
        blueAg.useUserEnergy(-10)
        print("I hope the rest was worth it")

'''
For the blue AI, this functions represents the blue bot. It reads the current state of the game/population.
Calculates how many voters there are and then chooses a message to send based on how much influence they have.
They also take into account their energy level and whether or not they want to send a spy and/or regain energy
and miss a turn. Once it chooses a message it returns a string saying what was done for later reference.

Returns: string
'''
def blueAI():
    isSpy = False
    action = ''
    current_voters, current_non_voters = calcVoters()

    if VERBOSE == True:
        print(f"\nBlue Agent Uncertainty Started at: {blueAg.uncertainty}\n")

    #Message of HIGHEST potency... biggest reward & risk
    def counter5():
        outcome = sendMsg(5, 0.1, 0.25,'blue', 0.7)
        action = "The Government have just completed a COUNTER RAID"
        return action, outcome

    #Message of second HIGHEST potency
    def counter4():
        outcome = sendMsg(4, 0.35, 0.25, 'blue', 0.5)
        action = "The Government have just completed a COUNTER PETITION"
        return action, outcome
   
    #Message of MEDIUM potency
    def counter3():
        outcome = sendMsg(3, 0.5, 0.4, 'blue', 0.3)
        action = "The Government have just handed out COUNTER FLYERS"
        return action, outcome

    #Message of second LOWEST potency
    def counter2():
        outcome = sendMsg(2, 0.65, 0.45, 'blue', 0.2)
        action = "The Government have just completed a COUNTER PROTEST"
        return action, outcome

    #Message of LOWEST potency... minimal risk & reward
    def counter1():
        outcome = sendMsg(1, 0.8, 0.45, 'blue', 0.1)
        action = "The Government have just posted a COUNTER VIDEO... and it's going viral"
        return action, outcome

    #Government takes no action this day/round... gains back energy
    def skipDay():
        if gamemode == 3 and VERBOSE == True:
            print("\t\tThe Government are resting to regain energy!\n")
        blueAg.useEnergy(-10)
        return True

    #Sends a spy into the population
    def sendSpy():
        if Probability.prob(spies[0].betray) == True:
            if gamemode == 1:
                print("\n>>> The Government has sent a Spy... Luckily he is one of ours")
            elif gamemode == 3 and VERBOSE == True:
                print("\t\tGovernment has been BETRAYED by a spy\n")
            if Probability.prob(0.1) == True:
                    #70% increase to favour uncertainty (Red Team)
                    new_uncertainty = greenAgents[i].uncertainty + (greenAgents[i].uncertainty * 0.7)
                    greenAgents[i].changeUncertainty(new_uncertainty)
        else:
            if gamemode == 1:
                print("\n>>> The Government broke into our system, we found a Spy")
            elif gamemode == 3 and VERBOSE == True:
                print("\t\tGovernment has successfully sent a spy\n")
            isSpy = True
            return isSpy

    #Government is considerably low on energy and have spies available... so will send a spy
    if blueAg.energy < 3 and len(spies) > 0:
        isSpy = sendSpy()
        spies.pop(0)

    # The Government are low on energy, out of agents and are still in control of the game (50% influence)
    # So they try to regain energy by missing days
    restDay = False
    if (num_spies == 0 and blueAg.energy <= 20) or (num_spies == 0 and blueAg.energy < 30 and current_voters >= 0.5*n):
        restDay = skipDay()
        action = "The Government are Resting... be prepared\n"

    #Decision Making Process
    #No energy is consumed if isSpy is True
    #Nothing happens if agent decides to rest
    if not restDay:    
        # Less than 15% of Population want to vote
        if current_voters <= (n*0.15):
            if 0.25 < blueAg.uncertainty <= 0.4:
                action, outcome = counter4()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(4, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(15)
                else:
                    isSpy = False
            elif 0.4 < blueAg.uncertainty <= 1:
                action, outcome = counter3()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(3, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(10)
                else:
                    isSpy = False
            else:
                action, outcome = counter5()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(5, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(20)
                else:
                    isSpy = False

        #Between 15% and 35% of Population want to vote
        elif current_voters > (n*0.15) and current_voters <= (n*0.35):
            if 0.2 < blueAg.uncertainty <= 0.4:
                action, outcome = counter3()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(3, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(10)
                else:
                    isSpy = False
            elif 0.4 < blueAg.uncertainty <= 1:
                action, outcome = counter2()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(2, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(5)
                else:
                    isSpy = False
            else:
                action, outcome = counter4()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(4, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(15)
                else:
                    isSpy = False

        #Between 35% and 65% of Population want to vote
        elif current_voters > (n*0.35) and current_voters <= (n*0.65):
                if 0.2 < blueAg.uncertainty <= 0.4:
                    action, outcome = counter2()
                    resulting_voters, useless = calcVoters()
                    if current_voters == resulting_voters:
                        agentUncertaintyChange(0, 'blue', outcome, True)
                    else:
                        agentUncertaintyChange(2, 'blue', outcome)

                    if isSpy == False:
                        blueAg.useEnergy(5)
                    else:
                        isSpy = False
                elif 0.4 < blueAg.uncertainty <= 1:
                    action, outcome = counter1()
                    resulting_voters, useless = calcVoters()
                    if current_voters == resulting_voters:
                        agentUncertaintyChange(0, 'blue', outcome, True)
                    else:
                        agentUncertaintyChange(1, 'blue', outcome)

                    if isSpy == False:
                        blueAg.useEnergy(2)
                    else:
                        isSpy = False
                else:
                    action, outcome = counter3()
                    resulting_voters, useless = calcVoters()
                    if current_voters == resulting_voters:
                        agentUncertaintyChange(0, 'blue', outcome, True)
                    else:
                        agentUncertaintyChange(3, 'blue', outcome)

                    if isSpy == False:
                        blueAg.useEnergy(10)
                    else:
                        isSpy = False

        #Between 65% and 85% of Population want to vote
        elif current_voters > (n*0.65) and current_voters <= (n*0.85):
            action, outcome = counter2()
            resulting_voters, useless = calcVoters()
            if current_voters == resulting_voters:
                agentUncertaintyChange(0, 'blue', outcome, True)
            else:
                agentUncertaintyChange(2, 'blue', outcome)

            if isSpy == False:
                blueAg.useEnergy(5)
            else:
                isSpy = False
        
        #Between 85% and 100% of Population want to vote
        elif current_voters > (n*0.85):
            #A 50% chance of getting cocky when dominating and sending a potent msg when they don't need to
            if blueAg.uncertainty < 0.2 and Probability.prob(0.5):
                action, outcome = counter5()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(5, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(25)
                else:
                    isSpy = False
            else:
                action, outcome = counter1()
                resulting_voters, useless = calcVoters()
                if current_voters == resulting_voters:
                    agentUncertaintyChange(0, 'blue', outcome, True)
                else:
                    agentUncertaintyChange(1, 'blue', outcome)

                if isSpy == False:
                    blueAg.useEnergy(2)
                else:
                    isSpy = False


    if VERBOSE == True:
        print(f"\nBlue Agent Uncertainty changed to: {blueAg.uncertainty}\n")
        print(f"The Governments Energy is currently at: {blueAg.energy}%\n")

    return action

'''
For the red AI, this functions represents the red bot. It reads the current state of the game/population.
Calculates how many voters there are and then chooses a message to send based on how much influence they have.
Once it chooses a message it returns a string saying what was done for later reference.

Returns: string
'''
def redAI():
    current_voters, current_non_voters = calcVoters()
    
    if VERBOSE == True:
        print(f"\nRed Agent Uncertainty Started at: {redAg.uncertainty}\n")
    #Message of HIGHEST potency... high reward & risk
    def msg5():
        outcome = sendMsg(5, 0.1, 0.25, 'red', 0.7)
        action = "The Resistance did their own experiments with MK-ULTRA and started the hippie era!"
        return action, outcome
    
    #Message of second HIGHEST potency
    def msg4():
        outcome = sendMsg(4, 0.35, 0.25, 'red', 0.5)
        action =  "The Resistance has created lies about your free HealthCare Scheme!"
        return action, outcome
   
    #Message of MEDIUM potency
    def msg3():
        outcome = sendMsg(3, 0.5, 0.4, 'red', 0.3)
        action =  "The Resistance have discovered your subliminal messages and exposing it to the masses!"
        return action, outcome

    #Message of second LOWEST potency
    def msg2():
        outcome = sendMsg(2, 0.65, 0.45, 'red', 0.2)
        action =  "The Resistance have raided your event and getting international media"
        return action, outcome

    #Message of LOWEST potency... low risk & reward
    def msg1():
        outcome = sendMsg(1, 0.8, 0.45, 'red', 0.1)
        action =  "The Resistance have just posted a COUNTER VIDEO... and it's going viral"
        return action, outcome
            
    #Decision making process
    #influence<15%
    if current_non_voters <= (n*0.15):
        if 0.4 < redAg.uncertainty <= 0.6:
            action, outcome  = msg4()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(4, 'red', outcome)
        elif 0.6 < redAg.uncertainty <= 1:
            action, outcome  = msg3()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(3, 'red', outcome)
        else:
            action, outcome  = msg5()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(5, 'red', outcome)
    # 15% < influence < 35%
    elif current_non_voters > (n*0.15) and current_non_voters <= (n*0.35):
        if 0.5 < redAg.uncertainty <= 0.7:
            action, outcome = msg3()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(3, 'red', outcome)
        elif 0.7 < redAg.uncertainty <= 1:
            action, outcome  = msg2()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(2, 'red', outcome)
        else:
            action, outcome  = msg4()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(4, 'red', outcome)
                
    # 35% < influence < 65%
    elif current_non_voters > (n*0.35) and current_non_voters <= (n*0.65):
        if 0.5 < redAg.uncertainty <= 0.7:
            action, outcome  = msg2()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(2, 'red', outcome)
        elif 0.7 < redAg.uncertainty <= 1:
            action, outcome  = msg1()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(1, 'red', outcome)
        else:
            action, outcome  = msg3()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(3, 'red', outcome)

    # 65% < influence < 85%
    elif current_non_voters > (n*0.65) and current_non_voters <= (n*0.85):
        action, outcome  = msg2()
        resulting_voters, useless = calcVoters()
        if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
        else:
            agentUncertaintyChange(2, 'red', outcome)

    # influence > 85%
    elif current_non_voters > (n*0.85):
        if redAg.uncertainty < 0.2 and Probability.prob(0.5):
            action, outcome  = msg5()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(5, 'red', outcome)
        else:
            action, outcome  = msg1()
            resulting_voters, useless = calcVoters()
            if resulting_voters == current_voters:
                agentUncertaintyChange(0, 'red', outcome, True)
            else:
                agentUncertaintyChange(1, 'red', outcome)

    if VERBOSE == True:
        print(f"\nRed Agent uncertainty change to: {redAg.uncertainty}\n")

    return action

def csvFile(num):
    f = open('csv' + str(num) + '.csv', 'w')
    writer = csv.writer(f)

    header = ['node uncertainty', 'vote status']

    writer.writerow(header)
    for i in range(n):
        if greenAgents[i].voteStatus == True:
            row = [greenAgents[i].uncertainty,1]
            writer.writerow(row)
        else:
            row = [greenAgents[i].uncertainty,0]
            writer.writerow(row)
    f.close()
        

    
round = 1
userEnergy = 100
blueExhaust = False

#This along with 2 others are spaced out for getting uncertainties at different points in the game
#One at the start, one in the middle and one at the end. They have been commented out, feel free to use them
#csvFile(1)

#Print out the intro to the specified game modes
if gamemode == 1:
    gamemode1Intro()
elif gamemode == 2:
    gamemode2Intro()
elif gamemode == 3:
    gamemode3Intro()

# Game Loop
if gamemode == 2 or gamemode == 1 or (gamemode == 3 and VERBOSE == True):
    print(f"\n\n{Fore.YELLOW}-------------------------- START STATE OF THE POPULATION --------------------------")
    roundSummary()

start = time.time() #get the time just before the game loop starts

while(round != days+1):
    #Playing as the Resistence
    if gamemode == 1:
        #Break out of the game loop if government run out of energy
        if blueAg.energy <= 0:
            blueExhaust = True
            break
        print(f"\n{Fore.YELLOW}-------------------------- Day {str(round)} --------------------------")
        redUserGameplay()
        gov_response = blueAI()
    #Playing as the Government
    elif gamemode == 2:
        #Break out of the game loop if government run out of energy
        if blueAg.usrEnergy <= 0:
            blueExhaust = True
            break
        print(f"\n{Fore.YELLOW}-------------------------- Day {str(round)} --------------------------")
        res_response = redAI()
        print(f"{Fore.RED}The Resistence Message: {Fore.WHITE}{res_response}\n")
        
        blueUserGameplay()
    #Running a Simulation
    elif gamemode == 3:
        #Break out of the game loop if government run out of energy
        if blueAg.energy <= 0:
            blueExhaust = True
            break
        if VERBOSE == True:
            print(f"\n{Fore.YELLOW}-------------------------- Day {str(round)} --------------------------")
            print(f"\n>>> {Fore.RED}RESISTANCE MESSAGE HAS BEEN SENT\n")
        res_response = redAI()
        if VERBOSE == True:
            print(f"\n>>> {Fore.BLUE}GOVERNMENTS COUNTER NARRATIVE HAS BEEN SENT\n")
        gov_response = blueAI()
        
    #Population Interaction
    graphEdges = edgeDict(g)
    greenNetworkInteraction(graphEdges)
    greenUcertaintyCheck()

    # if round == days/2:
    #     csvFile(2)

    if gamemode == 1:
        print(f"\n>>> {Fore.BLUE}GOVERNMENTS RESPONSE{Fore.WHITE}: {gov_response}\n")
        roundSummary()
    elif gamemode == 2:
        print(f"\n>>> {Fore.RED}RESISTANCE RESPONSE{Fore.WHITE}: {res_response}\n")
        roundSummary()
    elif gamemode == 3 and VERBOSE == True:
        roundSummary()

    round += 1

end = time.time() # get the time after the game loop finishes

#csvFile(3)

#Print out the Results of the game depending on the game mode
if gamemode == 1:
    gamemode1Summary(blueExhaust)
elif gamemode == 2:
    gamemode2Summary(blueExhaust)
elif gamemode == 3:
    gamemode3Summary(start, end, blueExhaust)
