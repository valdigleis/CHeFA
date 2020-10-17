#! -*- utf-8 -*-
#!/usr/bin/python3

from Machine import AFHT

from random import randint

class HeCA(object):
    """
    docstring
    """

    def __init__(self):
        self.__automata = []
        self.__U = []
        self.__nameD = None
        self.__alpha = 0.01
    
    def fit(self, X, y, clcs, distance='jac', alpha=0.1):
        self.__nameD = distance
        self.__alpha = alpha
        # Divide as palavras
        words = []
        for i in clcs:
            words.append(self.__separeWords(X, y, i))
        # Cria as máquinas
        for i in range(len(words)):
            L = words[i]
            A = AFHT(L)
            A.normalize()
            A.minimize(distance, alpha)
            self.__automata.append(A)
        Ta = self.__automata[0]
        mL = [self.__automata[i] for i in range(1, len(clcs))]
        # Cria a máquina da união
        self.__U = Ta.union(*mL)
    
    def predict(self, words):
        output = []
        for word in words:
            X = self.__U.computeValue(word)
            valueD = []
            for M in self.__automata:
                Y = M.computeValue(word)
                valueD.append(self.__calcDistance(X, Y))
            output.append(self.__computeClC(valueD))
        return output
    
    def __computeClC(self, valueD):
        d = min(valueD)
        cont = 0
        for V in valueD:
            if V == d:
                cont = cont + 1
        if cont < len(valueD):
            return valueD.index(d)
        else:
            return randint(0, len(valueD)-1)

    def __calcDistance(self, X, Y):
        if self.__nameD == 'jac':
            return X ** Y
        elif self.__nameD == 'std':
            return X / Y
        else:
            return X / Y

    def __separeWords(self, X, y, n):
        words = []
        for i in range(len(y)):
            if y[i] == n:
                words.append(X[i])
        return words