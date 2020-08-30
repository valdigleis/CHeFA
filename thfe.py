import pywt

class THFE:

    def __init__(self, values):
        self.__values = set()
        for x in values:
            if x > 1.0:
                self.__values.add(abs(1.0/x))
            elif x < 0.0:
                self.__values.add(abs(1.0/x))
            else:
                self.__values.add(x)

    def getValues(self):
        return self.__values

    def normalize(self, n):
        if len(self.__values) > n:
            vector = sorted(list(self.__values))
            T = len(vector)-1
            nList = list()
            for i in range(n):
                nList.append(vector[T - i])
            self.__values = set(nList)

    def __add__(self, other):
        result = set()
        for x in self.__values:
            for y in other.getValues():
                result.add(max(x, y))
        return THFE(result)

    def __mul__(self, other):
        result = set()
        for x in self.__values:
            for y in other.getValues():
                result.add(min(x, y))
        return THFE(result)

    def __floordiv__(self, other):
        """Metodo que implementa o calculo de distancia jaccard."""
        U = self.__values.union(other.getValues())
        I = self.__values.intersection(other.getValues())
        return len(I)/len(U)

    def __lshift__(self, other):
        '''Metodo que implementa a distancia média'''
        S = 0.0
        for x in self.__values:
            for z in other.getValues():
                S = S + abs(x - z)
        return S/(len(self.__values) * len(other.getValues()))

    def __str__(self):
        return str(self.__values)


def convertSignalToTHFE(inputSignal):
    valuesResolutions = list()
    wavelet = pywt.Wavelet('haar')
    n = pywt.dwt_max_level(len(inputSignal), wavelet)
    signal = inputSignal
    for i in range(n):
        cA, cB = pywt.dwt(signal, wavelet)
        for x in cA:
            valuesResolutions.append(x)
        signal = cA
    return THFE(valuesResolutions)



ONE = THFE([1.0])
ZERO = THFE([0.0])