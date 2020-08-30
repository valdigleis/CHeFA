from thfe import THFE
from thfe import ZERO
from thfe import ONE
from thfe import convertSignalToTHFE
from math import sqrt
from random import choice


class AFHT:

    def __init__(self, words, label):
        self.__label = label
        self.__states = set(['s0'])
        self.__alphabet = set()
        self.__s0 = 's0'
        self.__delta = dict()
        self.__F = dict()
        self.__defineDelta(words)
        self.__defineF(words)
        self.__normalize()

    def __defineDelta(self, words):
        for word in words:
            S = self.__s0
            for c in word:
                self.__alphabet.add(c)
                L = S + ',' + c
                if L in self.__delta:
                    S = self.__delta[L]
                else:
                    self.__delta[L] = 's' + str(len(self.__states))
                    S = self.__delta[L]
                    self.__states.add(S)

    def __defineF(self, words):
        useds = dict()
        for s in self.__states:
            useds[s] = list()
        for word in words:
            S = self.__s0
            states = set()
            for c in word:
                L = S + ',' + c
                S = self.__delta[L]
                states.add(S)
            for s in self.__states:
                if s in states:
                    useds[s].append(1.0)
                else:
                    useds[s].append(0.0)
        for s in self.__states:
            self.__F[s] = convertSignalToTHFE(useds[s])

    def __normalize(self):
        n = int(sqrt(len(self.__states)))
        for s in self.__states:
            self.__F[s].normalize(n)

    def __len__(self):
        return len(self.__states)

    def reduction(self, alpha=0.1, method='jaccard'):
        reds = set([self.__s0])
        blues = self.__getBlues(reds)
        while len(blues) > 0:
            blue = choice(list(blues))
            toRed = True
            for red in reds:
                if self.__isEquivalent(red, blue, alpha, method):
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
        for a in self.__alphabet:
            Lb = blue + ',' + a
            Lr = red  + ',' + a
            if Lb in self.__delta and Lr in self.__delta :
                s1 = self.__delta[Lr]
                s2 = self.__delta[Lb]
                self.__fold(s1, s2)
            elif Lb in self.__delta:
                s = self.__delta[Lb]
                self.__delta[Lr] = s
                del self.__delta[Lb]

    def __otimize(self):
        notAcess = self.__getNotAccessibles()
        toDel = list()
        for L in self.__delta:
            T = L.split(',')
            if T[0] in notAcess or self.__delta[L] in notAcess:
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

            
    def __getSource(self, q):
        for L in self.__delta:
            if self.__delta[L] == q:
                return L
        return None
    
    def __getBlues(self, reds):
        blues = set()
        for red in reds:
            for a in self.__alphabet:
                L = red + ',' + a
                if L in self.__delta:
                    if self.__delta[L] not in reds:
                        blues.add(self.__delta[L])
        return blues


    def __isEquivalent(self, q, p, alpha, method):
        if method == 'jaccard':
            return (self.__F[q] // self.__F[p]) <= alpha
        else:
            return (self.__F[q] << self.__F[p]) <= alpha




    def __str__(self):
        output = 'The machine ' + self.__label + ' is formed by:\n'
        S = 'S = ' + str(self.__states) + '\n'
        X = 'X = ' + str(self.__alphabet) + '\n'
        D = ''
        F = ''
        for key, value  in self.__delta.items():
            D = D + '\u03B4(' + key + ')=' + str(value) + '\n'
        for key, value in self.__F.items():
            #F = F + '\u03BC(' + key + ')=' + str(value) + '\n'
            F = F + 'F(' + key + ')=' + str(value) + '\n'
        output = output + S + X + self.__s0 + '\n' + D + F
        return output