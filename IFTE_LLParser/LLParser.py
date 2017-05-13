#All constants are indexed from 0
import sys

Term = 0
Rule = 1
Routine = 2

# Terminals
T_IF = 0
T_THEN = 1
T_ELSE = 2
T_NOTIFTE = 3
T_ENDIF = 4
T_END = 5

# Non-terminals
N_ALL = 0
N_TEXT = 1
N_IFTE = 2
N_BLOCK = 3
N_OPTELSE = 4

# Semantic Routines

R_STARTIF = 0
R_ENDIF = 1

# Parsing table

'''
        |  if  | then  | else | notifte | endif |  $  |
all     |  R0      -      -        R0       -      R7
text    |  R1      -      -        R2       -      R7
ifte    |  R3      -      -        -        -      -
block   |  R4      -      -        R5       -      -    
optelse |  -       -      R6       -        R7     -

'''
# Matrice con gli indici delle routine da lanciare in corrispondenza di term/n_term
table = [[0, -1, -1, 0, -1, 7],
         [1, -1, -1, 2, -1, 7],
         [3, -1, -1, -1, -1, -1],
         [4, -1, -1, 5, -1, -1],
         [-1, -1, 6, -1, 7, -1]]

# Rules matrix
rules = [[(Rule, N_TEXT), (Term, T_END)],                                                                           #0
         [(Rule, N_IFTE), (Rule, N_TEXT)],                                                                          #1
         [(Term, T_NOTIFTE), (Rule, N_TEXT)],                                                                       #2
         [(Term, T_IF), (Routine, R_STARTIF), (Term, T_NOTIFTE), (Term, T_THEN),
          (Rule, N_BLOCK), (Rule, N_OPTELSE), (Term, T_ENDIF), (Routine, R_ENDIF)],                                 #3
         [(Rule, N_IFTE)],                                                                                          #4
         [(Term, T_NOTIFTE)],                                                                                       #5
         [(Term, T_ELSE), (Rule, N_BLOCK)],                                                                         #6
         []]                                                                                                        #7                                                                                      #8
'''
<All> -> <Text> $ 
<Text> -> <Ifte> <Text> | <Not_Ifte> <Text> | epsilon
<Ifte> -> if <Not_Ifte> then <Block> <Opt_Else> endif
<Block> -> <Ifte> | <Not_Ifte> | epsilon
<Opt_Else> -> else <Block> | epsilon
'''

ifConstructsPositions = []
numIfOpen = 0
numEndifFound = 0

#Ritorna vero se non ho una delle keywords dell'if
def isIf(word) :
    if word == 'if' :
        return True
    return False

def isThen(word) :
    if word == 'then' :
        return True
    return False

def isElse(word) :
    if word == 'else' :
        return True
    return False

def isEndif(word) :
    if word == 'endif' :
        return True
    return False

def isWord(word):
    if isIf(word) or isThen(word) or isElse(word) or isEndif(word) :
        return False
    return True

#Definisco le routines semantiche

def rStartIf(position) :
    global numIfOpen
    numIfOpen += 1
    if numIfOpen == 1 :
        ifConstructsPositions.append(position)

def rEndIf(position) :
    global numEndifFound
    global numIfOpen
    numEndifFound += 1
    numIfOpen -= 1
    if numIfOpen == 0 :
        numEndifFound = 0

#Routine array
routines = [rStartIf, rEndIf]

stack = [(Rule, N_ALL)]

#Analisi lessicale genera token per frasi e divisore frasi, oltre a mettere
#in coda le frasi così trovate ritorna la lista di token
def lexicalAnalysis(inputstring):
    tokens = []
    for i,word in enumerate(inputstring.split()) :
        if isWord(word) :
            if(i > 0) :
                (numWord, tokenTemp) = tokens[-1]
                if (tokenTemp != T_NOTIFTE) : tokens.append((i,T_NOTIFTE))
            else :
                tokens.append((i,T_NOTIFTE))
        elif isIf(word) : tokens.append((i,T_IF))
        elif isThen(word) : tokens.append((i,T_THEN))
        elif isElse(word) : tokens.append((i,T_ELSE))
        elif isEndif(word): tokens.append((i,T_ENDIF))
    tokens.append((i,T_END))
    #print(tokens)
    return tokens

#Analisi sintattica top-down con supporto per routine semantiche
def syntacticAnalysis(tokens):
    position = 0
    while len(stack) > 0:
        (type, value) = stack.pop()
        (pos, token) = tokens[position]
        if type == Term:
            if value == token:
                position += 1
                #print('pop', value)
                if token == T_END :
                    print("Input accepted.")
                    print("Number of 'if' constructs recognised: {0}.".format(len(ifConstructsPositions)))
                    if len(ifConstructsPositions) != 0 :
                        for i,construct in enumerate(ifConstructsPositions) :
                            print("If construct number {0} found at {1}.\n".format(i+1,construct))
                    else :
                        print("No if constructs found.\n")

                    ifConstructsPositions.clear()
            else:
                print("Error: unexpected value (token index:{0}) at word n° {1}".format(token, pos + 1))
                break

        elif type == Rule:
            #print('value', value, 'token', token)
            rule = table[value][token]
            #print('rule', rule)
            for r in reversed(rules[rule]):
                stack.append(r)

        elif type == Routine:
            routines[value](pos)
            #print('routine', routines[value])
        #print('stack', stack)

input_file = "prova_5.txt"
print("Current file: " + input_file)
input_string = open(input_file).read()
syntacticAnalysis(lexicalAnalysis(input_string))