import ast
import numpy as np
import matplotlib.pyplot as plt

MP_results = {}
FO_results = {}

with open('Scalability/results/MP_results_2.txt', 'r') as file:
    MP_results = ast.literal_eval(file.read())
with open('Scalability/results/FO_results_2.txt', 'r') as file:
    FO_results = ast.literal_eval(file.read())


# Prepare Data for FO_results
mean_times_fo = [np.mean([run['time'] for run in instance.values()]) for instance in FO_results.values()]
std_dev_fo = [np.std([run['time'] for run in instance.values()]) for instance in FO_results.values()]
instances_fo = list(FO_results.keys())

# Prepare Data for MP_results
times_mp = [value['time'] for value in MP_results.values()]
instances_mp = list(MP_results.keys())

# Convert instances to string for plotting
instances_fo_str = [str(instance) for instance in instances_fo]
instances_mp_str = [str(instance) for instance in instances_mp]

# Plotting
plt.figure(figsize=(10, 5))

# Plot FO_results with error bars
plt.errorbar(instances_fo_str, mean_times_fo, yerr=std_dev_fo, fmt='-o', label='FO Mean Time', capsize=5)

# Plot MP_results
plt.plot(instances_mp_str, times_mp, '-s', label='MP Time')

# Adjustments
plt.xticks(rotation=45)
plt.xlabel('Instance')
plt.ylabel('Time (s)')
plt.title('Comparison of Mean Time with Standard Deviation (FO) and Time (MP)')
plt.legend()
plt.tight_layout()
plt.show()