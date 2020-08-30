import os
import numpy as np

class Dataset:

    def __init__(self, urlFile):
        fileData = open(urlFile, 'r')
        self.__attributes = list()
        self.__classes = list()
        for line in fileData:
            L = line.replace('\n', '')
            # remove os atributos faltantes
            L = L.replace('?,', '')
            L = L.replace(',?,', ',')
            k = len(L)
            if k > 1:
                # Pega os index da classe e salva
                T = -1
                for i in reversed(range(k)):
                    if L[i] == ',':
                        T = i
                        break
                atr = ''
                clc = ''
                for i in range(k):
                    if i < T:
                        atr = atr + L[i] 
                    elif i > T:
                        clc = clc + L[i]
                self.__attributes.append(atr)
                self.__classes.append(clc)
    
    def getNumAttributes(self):
        n = 0
        j = -1
        for i in range(len(self.__attributes)):
            if len(self.__attributes[i]) > n:
                n = len(self.__attributes[i])
                j = i
        c = 0
        for i in self.__attributes[j]:
            if i == ',':
                c = c + 1
        return c + 1

    def getAllAttributes(self):
        L = list()
        for w in self.__attributes:
            L.append(w.replace(',', ''))
        return L
                
    def __str__(self):
        line = ''
        for i in range(len(self.__classes)):
            line = line + (self.__attributes[i] + ',' + self.__classes[i] + '\n')
        return line