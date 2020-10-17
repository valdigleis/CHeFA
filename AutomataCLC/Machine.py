#! -*- utf-8 -*-
#!/usr/bin/python3

from THEFE import THFE
from THEFE import ZERO
from THEFE import ONE
from THEFE import convertSignalToTHFE as GTHFE

from math import log2
from math import sqrt

from random import choice

import itertools

class AFHT(object):
    """
    Classe que implementa os PAFHTD.
    """
    def __init__(self, words):
        self.__s0 = frozenset(['s0'])
        self.__states = set([self.__s0])
        self.__delta = dict()
        self.__alphabet = set()
        self.__F = dict()
        if len(words) > 0:
            self.__setTransitions(words)
            self.__valuation(words)
        else:
            self.__F[self.__s0] = ZERO

    def __setTransitions(self, words):
        for word in words:
            S = self.__s0
            for c in word:
                L = (S, c)
                self.__alphabet.add(c)
                if L not in self.__delta:
                    p = 's' +str(len(self.__states))
                    self.__delta[L] = frozenset([p])
                S = self.__delta[L]
                self.__states.add(S)

    def __valuation(self, words):
        if len(words) > 0:
            use = dict()
            for s in self.__states:
                use[s] = list()
            for word in words:
                S = self.__s0
                Ls = []
                for c in word:
                    L = (S, c)
                    S = self.__delta[L]
                    Ls.append(S)
                for s in self.__states:
                    if s in Ls:
                        use[s].append(1.0)
                    else:
                        use[s].append(0.0)
            if not log2(len(words)).is_integer():
                n = len(words)
                while not log2(n).is_integer():
                    n = n + 1
                d = n - len(words)
                for s in self.__states:
                    for i in range(d):
                        use[s].append(0.0)
            for s in self.__states:
                signal = use[s]
                self.__F[s] = GTHFE(signal)

    def compute(self, word):
        S = self.__s0
        for c in word:
            L = (S,  c)
            if L in self.__delta:
                S = self.__delta[L]
            else:
                return None
        return S

    def computeValue(self, word):
        S = self.compute(word)
        if S != None:
            return self.__F[S]
        else:
            return ZERO

    def getLabel(self):
        return self.__label

    def getInfos(self):
        return self.__states, self.__alphabet, self.__delta, self.__s0, self.__F

    def setInfos(self, S, A, D, s0, F):
        self.__states, self.__alphabet, self.__delta, self.__s0, self.__F = S, A, D, s0, F    

    def renameStates(self, label):
        nS = set()
        for S in self.__states:
            S1 = set()
            for s in S:
                tmp = s.replace('s', label)
                S1.add(tmp)
            NS = frozenset(S1)
            nS.add(NS)
        nDelta = dict()
        for K, V in self.__delta.items():
            sK = set()
            for s in K[0]:
                tmp = s.replace('s', label)
                sK.add(tmp)
            P = frozenset(sK)
            c = K[1]
            sK = set()
            for s in V:
                tmp = s.replace('s', label)
                sK.add(tmp)
            Q = frozenset(sK)
            T = (P, c)
            nDelta[T] = Q
        nF = dict()
        for K, V in self.__F.items():
            sK = set()
            for s in K:
                tmp = s.replace('s', label)
                sK.add(tmp)
            sR = frozenset(sK)
            nF[sR] = V
        nS0 = set()
        for s in self.__s0:
            tmp = s.replace('s', label)
            nS0.add(tmp)
        self.setInfos(nS, self.__alphabet, nDelta, frozenset(nS0), nF)
        
    def union(self, *automata):
        '''
            Realiza a união com uma familia finita de automatos
        '''
        # Preparação
        list_State = [self.__states]
        list_Alphabet = [self.__alphabet]
        list_Delta = [self.__delta]
        list_S0 = [self.__s0]
        list_F = [self.__F]
        for i in range(len(automata)):
            S, A, D, s0, F = automata[i].getInfos()
            list_State.append(S)
            list_Alphabet.append(A)
            list_Delta.append(D)
            list_S0.append(s0)
            list_F.append(F)
        # Define o novo estado inicial
        nS0 = tuple(list_S0)
        # Define o alfabeto
        nA = set()
        for X in list_Alphabet:
            nA = nA.union(X)
        # Define o estado
        nS = set()
        nS.add(nS0)
        # Define o delta
        nD = dict()
        toUse = set([nS0])
        used = set()
        while len(toUse) > 0:
            P = choice(list(toUse))
            used.add(P)
            for c in nA:
                states = []
                for i in range(len(P)):
                    s = P[i]
                    T = (s, c)
                    delta = list_Delta[i]
                    if T in delta:
                        states.append(delta[T])
                    else:
                        states.append(frozenset(set()))
                nP = tuple(states)
                key = (P, c)
                nD[key] = nP
                nS.add(nP)
                if nP not in used:
                    toUse.add(nP)
            toUse.remove(P)
        # Define o estado final
        nF = dict()
        for S in nS:
            value = ZERO
            for i in range(len(S)):
                s = S[i]
                if len(s) > 0:
                    Fi = list_F[i]
                    value = value + Fi[s]
            nF[S] = value
        words = []
        aut = AFHT(words)
        aut.setInfos(nS, nA, nD, nS0, nF)
        return aut

    def normalize(self):
        '''
            Realiza a beta normalização para o CHFT de estados finais.
        '''
        n = int(sqrt(len(self.__states)))
        for s in self.__states:
            self.__F[s].betaNormalization(n)

    def minimize(self, distance='jac', alpha=0.01):
        if len(self) > 1:
            reds = set([self.__s0])
            blues = self.__getBlues(reds)
            while len(blues) > 0:
                blue = choice(list(blues))
                toRed = True
                for red in reds:
                    if self.__isEquivalent(red, blue, alpha, distance):
                        toRed = False
                        self.__merge(red, blue)
                        self.__otimize()
                        break
                if toRed == True:
                    reds.add(blue)
                blues = self.__getBlues(reds)

    def __merge(self, red, blue):
        L = self.__getSource(blue)
        if L != None:
            self.__delta[L] = red
            self.__fold(red, blue)

    def __fold(self, red, blue):
        self.__F[red] = self.__F[red] + self.__F[blue]
        for c in self.__alphabet:
            Lb = (blue, c)
            Lr = (red, c)
            if Lb in self.__delta and Lr in self.__delta:
                s1 = self.__delta[Lr]
                s2 = self.__delta[Lb]
                self.__fold(s1, s2)
            elif Lb in self.__delta:
                s = self.__delta[Lb]
                self.__delta[Lr] = s
                del self.__delta[Lb]

    def __getSource(self, S):
        for L in self.__delta:
            if self.__delta[L] == S:
                return L
        return None
    
    '''
    def __isEquivalent(self, red, blue, alpha, distance):
        if distance == 'jac':
            if self.__F[red] ** self.__F[blue] > alpha:
                return False
            for c in self.__alphabet:
                T1 = (red, c)
                T2 = (blue, c)
                if T1 in self.__delta and T2 in self.__delta:
                    if self.__F[self.__delta[T1]] ** self.__F[self.__delta[T2]] > alpha:
                        return False
            return True
        elif distance == 'std':
            if self.__F[red] / self.__F[blue] > alpha:
                return False
            for c in self.__alphabet:
                T1 = (red, c)
                T2 = (blue, c)
                if T1 in self.__delta and T2 in self.__delta:
                    if self.__F[self.__delta[T1]] / self.__F[self.__delta[T2]] > alpha:
                        return False
            return True
        else:
            if self.__F[red] // self.__F[blue] > alpha:
                return False
            for c in self.__alphabet:
                T1 = (red, c)
                T2 = (blue, c)
                if T1 in self.__delta and T2 in self.__delta:
                    if self.__F[self.__delta[T1]] // self.__F[self.__delta[T2]] > alpha:
                        return False
            return True
    '''

    def __isEquivalent(self, red, blue, alpha, distance):
        if distance == 'jac':
            return (self.__F[red] ** self.__F[blue]) <= alpha
        elif distance == 'std':
            return (self.__F[red] / self.__F[blue]) <= alpha
        else:
            return (self.__F[red] // self.__F[blue]) <= alpha


    def __otimize(self):
        '''
            Remove todos os estados inacessiveis
        '''
        notAcess = self.__getNotAccessibles()
        toDel = list()
        for L in self.__delta:
            T = L[0]
            if T in notAcess or self.__delta[L] in notAcess:
                toDel.append(L)
        for L in toDel: 
            del self.__delta[L]
        for s in notAcess:
            del self.__F[s]
        self.__states = self.__states - notAcess

    def __getNotAccessibles(self):
        useds = set()
        toUse = set([self.__s0])
        while len(toUse) > 0:
            nextS = self.__getBlues(toUse)
            for s in toUse:
                useds.add(s)
            toUse = set()
            for s in nextS:
                if s not in useds:
                    toUse.add(s)
        notAccess = self.__states - useds
        return notAccess

    def __getBlues(self, reds):
        blues = set()
        for c in self.__alphabet:
            for red in reds:
                key = (red, c)
                if key in self.__delta:
                    S = self.__delta[key]
                    if S not in reds:
                        blues.add(S)
        return blues

    def __len__(self):
        return len(self.__states)

    def __str__(self):
        S = str(self.__states) + '\n'
        A = str(self.__alphabet) + '\n' + str(self.__s0) + '\n'
        D = ''
        for L, V in self.__delta.items():
            D = D + ('d(' + str(L) + ')=' + str(V)) + '\n'
        F = ''
        for L, V in self.__F.items():
            F = F + ('F(' + str(L) + ')=' + str(V)) + '\n'
        return S + A + D + F
        