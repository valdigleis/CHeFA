import pywt

class THFE(object):
    
    def __init__(self, values):
        if (isinstance(values, set) or isinstance(values, list)) and len(values) > 0:
            self.__degrees = set()
            for value in values:
                if not isinstance(value, float):
                    print("Value:", value, "is not of float type!")
                    self.__degrees = None
                    break
                elif value < 0.0 or value > 1.0:
                    print("Value:", value, "does not belong to [0,1]!")
                    self.__degrees = None
                    break
                else:
                    self.__degrees.add(value)
        elif isinstance(values, float):
            if values >= 0.0 and values <= 1.0:
                self.__degrees = set()
                self.__degrees.add(values)
            else:
                print("Value:", values, "does not belong to [0,1]!") 
                self.__degrees = None
        else:
            print(type(values))
            print(str(values))
            print("Invalid argument!")
            self.__degrees = None

    def betaNormalization(self, num):
        if len(self.__degrees) > num:
            signal = list(self.__degrees)
            signal.sort()
            newSignal = list()
            k =  len(self.__degrees) - num
            for i in range(len(self.__degrees)):
                if i >= k:
                    newSignal.append(signal[i])
            self.__degrees = set(newSignal)

    def notIsValid(self):
        return self.__degrees == None

    def getDegrees(self):
        return self.__degrees

    def getMean(self):
        S = 0.0
        for x in self.__degrees:
            S = S + x
        return S/len(self.__degrees)
    
    def __getListDegrees(self):
        """Metodo que retorna o conjunto de valores de pertinencia do elemento fuzzy hesistante tipico."""
        values = list()
        for x in self.__degrees:
            values.append(x)
        return values

    def __len__(self):
        return len(self.__degrees)

    def __str__(self):
        return str(self.__degrees)

    def __add__(self, other):
        """Metodo que implementa a max combinacao"""
        result = set()
        for x in self.__degrees:
            for y in other.getDegrees():
                result.add(max(x, y))
        return THFE(result)

    def __mul__(self, other):
        """Metodo que implementa a min combinacao."""
        result = set()
        for x in self.__degrees:
            for y in other.getDegrees():
                result.add(min(x, y))             
        return THFE(result)

    def __mod__(self, other):
        """Metodo que implementa a union combinacao."""
        L = list()
        for x in self.__degrees:
            L.append(x)
        for x in other.getDegrees():
            L.append(x)
        return THFE(L)

    def __eq__(self, other):
        """Metodo que implementa o teste de igualdade"""
        return self.__degrees == other.getDegrees()

    def __floordiv__(self, other):
        """Metodo que implementa o calculo de distancia padrao entre conjuntos."""
        m1 = min(self.__degrees)
        m2 = max(self.__degrees)
        n1 = min(other.getDegrees())
        n2 = max(other.getDegrees())
        L = [abs(m1 - n1), abs(m1 - n2), abs(m2 - n1), abs(m2 - n2)]
        return max(L)

    def __truediv__(self, other):
        '''Metodo que implementa a distancia média'''
        S = 0.0
        for x in self.__degrees:
            for z in other.getDegrees():
                S = S + abs(x - z)
        n = (len(self) * len(other))
        return S/n

    def __pow__(self, other):
        '''Metodo que calcula a distancia de Jaccard'''
        n = len(self.__degrees.intersection(other.getDegrees()))
        m = len(self.__degrees.union(other.getDegrees()))
        return 1.0 - (n/m)

    def __le__(self, other):
        S = other.getDegrees()
        s2 = max(S)
        s1 = max(self.__degrees)
        if self.__degrees.issubset(S) or (self.__degrees == S):
            return True
        elif s1 <= s2:
            return True
        else:
            return False

ONE = THFE([1.0])
ZERO = THFE([0.0])

def convertSignalToTHFE(signal):
    valuesResolutions = []
    wavelet = pywt.Wavelet('haar')
    n = pywt.dwt_max_level(len(signal), wavelet)
    X = signal
    for i in range(n):
        R = pywt.dwt(X, wavelet)
        for x in R[0]:
            valuesResolutions.append(x/1.0)
        X = R[0]
    return THFE(normalize(valuesResolutions))

def normalize(values):
    maxV = max(values)
    minV = min(values)
    signal = []
    for x in values:
        if maxV != minV:
            z = abs(x - minV)/(maxV - minV)
            signal.append(z)
        else:
            signal.append(0.0)
    return signal