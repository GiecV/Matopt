import ast
import numpy as np
import matplotlib.pyplot as plt

FO_results = {}

with open('Scalability/results/FO_results_2.txt', 'r') as file:
    FO_results = ast.literal_eval(file.read())


# Prepare Data for FO_results
mean_times_fo = [np.mean([np.abs(run['gap']) for run in instance.values()]) for instance in FO_results.values()]
std_dev_fo = [np.std([np.abs(run['gap']) for run in instance.values()]) for instance in FO_results.values()]
instances_fo = list(FO_results.keys())

# Convert instances to string for plotting
instances_fo_str = [str(instance) for instance in instances_fo]

# Plotting
plt.figure(figsize=(10, 5))

# Plot FO_results with error bars
# plt.errorbar(instances_fo_str, mean_times_fo, yerr=std_dev_fo, fmt='-o', label='FO Mean Time', capsize=5, color='red')
plt.plot(instances_fo_str, mean_times_fo, '-o', label='FO Mean Time', color='red')
plt.fill_between(instances_fo_str, np.array(mean_times_fo) - np.array(std_dev_fo),
                 np.array(mean_times_fo) + np.array(std_dev_fo), color='red', alpha=0.2)

# Adjustments
plt.xticks(rotation=45)
plt.xlabel('(N,M)')
plt.ylabel('Gap (%)')
plt.title('Gap of FO Heuristic')
plt.legend()
plt.tight_layout()
plt.show()