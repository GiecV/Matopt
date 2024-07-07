from prettytable import PrettyTable 
import numpy as np
import matplotlib.pyplot as plt
import ast

# Initialize variables
IP_results = {}
MP_results = {}
FO_results = {}

# Open and read the file
with open('Scalability/results/IP_results.txt', 'r') as file:
    IP_results = ast.literal_eval(file.read())
with open('Scalability/results/MP_results.txt', 'r') as file:
    MP_results = ast.literal_eval(file.read())
with open('Scalability/results/FO_results.txt', 'r') as file:
    FO_results = ast.literal_eval(file.read())

IP_best_results = {}
MP_best_results = {}
FO_best_results = {}

IP_avg_results = {}
MP_avg_results = {}
FO_avg_results = {}

for instance in IP_results:
    for run in IP_results[instance]:
        IP_results[instance][run]['gap'] = np.abs(IP_results[instance][run]['gap'])

for instance in MP_results:
    for run in MP_results[instance]:
        MP_results[instance][run]['gap'] = np.abs(MP_results[instance][run]['gap'])

for key, values in IP_results.items():
    best = min(values, key=lambda x: values[x]['time'])
    IP_best_results[key] = values[best]['time']

    mean = np.mean([values[x]['time'] for x in values])
    std_deviation = np.std([values[x]['time'] for x in values])
    IP_avg_results[key] = {'mean': mean, 'std_deviation': std_deviation}

for key, values in MP_results.items():
    best = min(values, key=lambda x: values[x]['time'])
    MP_best_results[key] = values[best]['time']

    mean = np.mean([values[x]['time'] for x in values])
    std_deviation = np.std([values[x]['time'] for x in values])
    MP_avg_results[key] = {'mean': mean, 'std_deviation': std_deviation}

for key, values in FO_results.items():
    best = min(values, key=lambda x: values[x]['time'])
    FO_best_results[key] = values[best]['time']

    mean = np.mean([values[x]['time'] for x in values])
    std_deviation = np.std([values[x]['time'] for x in values])
    FO_avg_results[key] = {'mean': mean, 'std_deviation': std_deviation}

for case in IP_best_results:
    IP_best_results[case] = round(IP_best_results[case], 4)
    IP_avg_results[case]['mean'] = round(IP_avg_results[case]['mean'], 4)
    IP_avg_results[case]['std_deviation'] = round(IP_avg_results[case]['std_deviation'], 4)
    MP_best_results[case] = round(MP_best_results[case], 4)
    MP_avg_results[case]['mean'] = round(MP_avg_results[case]['mean'], 4)
    MP_avg_results[case]['std_deviation'] = round(MP_avg_results[case]['std_deviation'], 4)
    FO_best_results[case] = round(FO_best_results[case], 4)
    FO_avg_results[case]['mean'] = round(FO_avg_results[case]['mean'], 4)
    FO_avg_results[case]['std_deviation'] = round(FO_avg_results[case]['std_deviation'], 4)

table = PrettyTable()
headers = ['M', 'N', 'IP Best', 'IP Mean', 'IP StdDev', 'MP Best', 'MP Mean', 'MP StdDev', 'FO Best', 'FO Mean', 'FO StdDev']
table.field_names = headers
for case in IP_best_results:

    m = case[1]
    n = case[0]
    alg1_best = IP_best_results[case]
    alg1_mean = IP_avg_results[case]['mean']
    alg1_stddev = IP_avg_results[case]['std_deviation']
    alg2_best = MP_best_results[case]
    alg2_mean = MP_avg_results[case]['mean']
    alg2_stddev = MP_avg_results[case]['std_deviation']
    alg3_best = FO_best_results[case]
    alg3_mean = FO_avg_results[case]['mean']
    alg3_stddev = FO_avg_results[case]['std_deviation']
    
    table.add_row([m, n, alg1_best, alg1_mean, alg1_stddev, alg2_best, alg2_mean, alg2_stddev, alg3_best, alg3_mean, alg3_stddev])

print(table)

# Step 1: Prepare Data
plot_data = {}

# Step 2: Extract Data
for case in IP_avg_results:
    n, m = case
    if (n, m) not in plot_data:
        plot_data[(n, m)] = {'IP': {'mean': None, 'std_dev': None}, 'MP': {'mean': None, 'std_dev': None}}
    plot_data[(n, m)]['IP']['mean'] = IP_avg_results[case]['mean']
    plot_data[(n, m)]['IP']['std_dev'] = IP_avg_results[case]['std_deviation']
    plot_data[(n, m)]['MP']['mean'] = MP_avg_results[case]['mean']
    plot_data[(n, m)]['MP']['std_dev'] = MP_avg_results[case]['std_deviation']

# Sort the data by instance size (N, M)
sorted_keys = sorted(plot_data.keys(), key=lambda x: x[1] * x[0] ** 2)

# Convert sorted data to lists for plotting
n_m_labels = [f"({key[0]}, {key[1]})" for key in sorted_keys]
ip_means = [plot_data[key]['IP']['mean'] for key in sorted_keys]
mp_means = [plot_data[key]['MP']['mean'] for key in sorted_keys]
ip_best_times = [IP_best_results[key] for key in sorted_keys]
ip_std_devs = [plot_data[key]['IP']['std_dev'] for key in sorted_keys]
mp_std_devs = [plot_data[key]['MP']['std_dev'] for key in sorted_keys]
mp_best_times = [MP_best_results[key] for key in sorted_keys]

n_m_labels = n_m_labels[:6]
ip_means = ip_means[:6]
mp_means = mp_means[:6]
ip_best_times = ip_best_times[:6]
ip_std_devs = ip_std_devs[:6]
mp_best_times = mp_best_times[:6]
mp_std_devs = mp_std_devs[:6]


# Step 3: Plotting
plt.figure(figsize=(5, 5))

# Plot IP model
plt.plot(n_m_labels, ip_means, '-o', color='blue', label='IP')
plt.fill_between(n_m_labels, np.array(ip_means) - np.array(ip_std_devs), np.array(ip_means) + np.array(ip_std_devs), color='blue', alpha=0.2)
plt.plot(n_m_labels, ip_best_times, 'x', color='darkblue', label='IP Best')

# Plot MP model
plt.plot(n_m_labels, mp_means, '-o', color='green', label='MP')
plt.fill_between(n_m_labels, np.array(mp_means) - np.array(mp_std_devs), np.array(mp_means) + np.array(mp_std_devs), color='green', alpha=0.2)
plt.plot(n_m_labels, mp_best_times, 'x', color='darkgreen', label='MP Best')

plt.ylim(-0.5,1)

plt.xlabel('(N, M)')
plt.ylabel('Average Time (s)')
plt.title('Average Time for IP and MP Models')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
