import math

def mean_difference_avg(values1, values2, isAbs):
    if isAbs:
        differences = [abs(values2[i] - values1[i]) for i in range(len(values2))] # List containing the absolute difference for each value between the second and the first dataset
    else:
        differences = [values2[i] - values1[i] for i in range(len(values2))] # List containing the difference for each value between the second and the first dataset
    
    mean_difference = sum(differences) / len(differences) # Compute the mean of the differences vector, with or without absolute value
    return mean_difference

def root_mean_squared_difference(values1, values2):
    squared_diff = [pow(values2[i],2) - pow(values1[i],2) for i in range(len(values2))] # Difference between the squared i-th value of the second dataset and the squared i-th value of the first
    mean_squared_diff = sum(squared_diff) / len(squared_diff) # Compute the mean of the squared differences
    return math.sqrt(abs(mean_squared_diff)) # Return the square root of the absolute value of the mean squared difference