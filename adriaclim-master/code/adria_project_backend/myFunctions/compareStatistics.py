import math

def mean_difference_avg(values1, values2, isAbs):
    if isAbs:
        differences = [abs(values2[i] - values1[i]) for i in range(len(values2))] #lista che contiene il valore assoluto della differenza di ogni valore tra il secondo e il primo dataset
    else:
        differences = [values2[i] - values1[i] for i in range(len(values2))] #lista che contiene la differenza di ogni valore tra il secondo e il primo dataset
    
    mean_difference = sum(differences) / len(differences) #calcola la media del vettore differences, con il valore assoluto o meno
    return mean_difference

def root_mean_squared_difference(values1, values2):
    squared_diff = [pow(values2[i],2) - pow(values1[i],2) for i in range(len(values2))] #diff tra l'i-esimo valore al quadrato del secondo e l'i-esimo valore al quadrato del primo
    mean_squared_diff = sum(squared_diff) / len(squared_diff) #calcolo della media del risultato ottenuto
    return math.sqrt(abs(mean_squared_diff)) #radice quadrata della media calcolata
