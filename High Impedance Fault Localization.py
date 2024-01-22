#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import csv
from sklearn import datasets, svm
from matplotlib.ticker import FormatStrFormatter
from sklearn.inspection import DecisionBoundaryDisplay


# In[2]:


# Pick some high impedance fault data for classification
file_paths = ['IEEE123_PV_L1C1B5HIF.csv', 'IEEE123_PV_L1C1B34HIF.csv', 'IEEE123_PV_L1C1B45HIF.csv']

data_dict = {}

for path in file_paths:
    # Read csv file
    data = np.genfromtxt(path, delimiter=',')    
    # Delete the first 3 rows
    data = data[3:]    
    # Select one part of the trajectory for voltage (column index 1) and current (column index 5), one phase
    selected_V = data[8000:8166, 1]
    selected_I = data[8000:8166, 5]    
    # Store selected data in dict
    data_dict[path] = {'V': selected_V, 'I': selected_I}

V_A = data_dict['IEEE123_PV_L1C1B5HIF.csv']['V']
V_B = data_dict['IEEE123_PV_L1C1B34HIF.csv']['V']
V_C = data_dict['IEEE123_PV_L1C1B45HIF.csv']['V']

I_A = data_dict['IEEE123_PV_L1C1B5HIF.csv']['I']
I_B = data_dict['IEEE123_PV_L1C1B34HIF.csv']['I']
I_C = data_dict['IEEE123_PV_L1C1B45HIF.csv']['I']


# In[3]:


def add_noise(signal, noise_percentage):
    noise = np.random.normal(0, noise_percentage / 100 * np.abs(signal), len(signal))
    noisy_signal = signal + noise
    return noisy_signal

# Generate samples with noises
num_samples = 300
noise_percentage_V = 2  # Fluctuation percentage for voltage
noise_percentage_I = 1.5  # Fluctuation percentage for current

# Generate samples with noise for each signal
V_A_samples = [add_noise(V_A, noise_percentage_V) for _ in range(num_samples)]
V_B_samples = [add_noise(V_B, noise_percentage_V) for _ in range(num_samples)]
V_C_samples = [add_noise(V_C, noise_percentage_V) for _ in range(num_samples)]

I_A_samples = [add_noise(I_A, noise_percentage_I) for _ in range(num_samples)]
I_B_samples = [add_noise(I_B, noise_percentage_I) for _ in range(num_samples)]
I_C_samples = [add_noise(I_C, noise_percentage_I) for _ in range(num_samples)]

V_concatenated = np.concatenate((V_A_samples, V_B_samples, V_C_samples), axis=0)
I_concatenated = np.concatenate((I_A_samples, I_B_samples, I_C_samples), axis=0)


# In[4]:


y_values = []

for i in range(num_samples * 3):  # Loop over all samples to calculate y values

    I_sample = I_concatenated[i]
    V_sample = V_concatenated[i]

    # The indices of break points
    xa_idx = 165  # 166-1
    xb_idx = 99    # 100-1
    xc_idx = 69    # 70-1
    xd_idx = 0     # 1-1

    # Break points for approximation
    xa = I_sample[xa_idx]
    xb = I_sample[xb_idx]
    xc = I_sample[xc_idx]
    xd = I_sample[xd_idx]

    # Define matrix A and linear coefficients b
    A1 = np.zeros((67, 4))
    A2 = np.zeros((31, 4))
    A3 = np.zeros((70, 4))
    b = []

    for j in range(100, 167):
        A1[j-100, 0] = ((xb - I_sample[j-1]) / (xb - xa))
        A1[j-100, 1] = ((I_sample[j-1] - xa) / (xb - xa))
        b.append(V_sample[j-1])

    for j in range(70, 101):
        A2[j-70, 1] = ((xc - I_sample[j-1]) / (xc - xb))
        A2[j-70, 2] = ((I_sample[j-1] - xb) / (xc - xb))
        b.append(V_sample[j-1])

    for j in range(1, 71):
        A3[j-1, 2] = ((xd - I_sample[j-1]) / (xd - xc))
        A3[j-1, 3] = ((I_sample[j-1] - xc) / (xd - xc))
        b.append(V_sample[j-1])

    # Concatenate matrices A1, A2, A3
    A = np.concatenate((A1, A2, A3), axis=0)
    
    b = np.array(b)

    # Closed-form solution of LS approximation
    A_transpose = np.transpose(A)
    y_i = np.linalg.lstsq(A_transpose @ A, A_transpose @ b, rcond=None)[0]

    y_values.append(y_i)
    
y_values = np.array(y_values)


# In[5]:


slope_matrix = np.zeros((num_samples*3, 4))

# Calculate slope rates
for i in range(0, num_samples*3):
    slope_matrix[i, 0] = (y_values[i, 1] - y_values[i, 0]) / (I_concatenated[i, xb_idx] - I_concatenated[i, xa_idx])
    slope_matrix[i, 1] = (y_values[i, 2] - y_values[i, 1]) / (I_concatenated[i, xc_idx] - I_concatenated[i, xb_idx])
    slope_matrix[i, 2] = (y_values[i, 3] - y_values[i, 2]) / (I_concatenated[i, xd_idx] - I_concatenated[i, xc_idx])
    
    if i <= num_samples-1:
        slope_matrix[i, 3] = 5
    elif num_samples <= i <= num_samples*2-1:
        slope_matrix[i, 3] = 34
    else:
        slope_matrix[i, 3] = 45


for element in slope_matrix:
    print(element)


# In[6]:


data = slope_matrix;

# First two columns as SVM input
X = data[:, :2]
# 4th columns as SVM output
y = data[:, 3]


# In[7]:


C = 1.0  # SVM regularization parameter
models = (
    svm.SVC(kernel="linear", C=C),
    svm.SVC(kernel="poly", degree=2, gamma="auto", C=C),
)
models = (clf.fit(X, y) for clf in models)

titles = (
    "SVM with linear kernel",
    "SVM with polynomial kernel",
)

fig, sub = plt.subplots(1, 2, figsize=(9, 4))
plt.subplots_adjust(wspace=0.3, hspace=0.2)

X0, X1 = X[:, 0], X[:, 1]

for clf, title, ax in zip(models, titles, sub.flatten()):
    disp = DecisionBoundaryDisplay.from_estimator(
        clf,
        X,
        response_method="predict",
        cmap=plt.cm.coolwarm,
        alpha=0.4,
        ax=ax,
        xlabel='s1',
        ylabel='s2',
    )
    ax.scatter(X0, X1, c=y, cmap=plt.cm.coolwarm, s=20, edgecolors="k")
    ax.set_xticks(())
    ax.set_yticks(())
    ax.set_title(title)
    
    ax.set_xticks(np.linspace(X0.min(), X0.max(), 4))
    ax.set_yticks(np.linspace(X1.min(), X1.max(), 5))
    
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))

plt.show()

