# -*- coding: utf-8 -*-
"""Tubes_Swarm_PSO.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16Q99Id-nP8SkZXebyDAmMZGtfvlY8NM2

# Penerapan Efisiensi Particle Swarm Optimization Dengan Naive Bayes Dalam Klasifikasi Penyakit Diabetes

## library
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score
import random
import math
import copy
import sys

"""## Dataset"""

df=pd.read_csv("/content/drive/MyDrive/TUBES/diabetes.csv")
df.head()

"""## Ekplorasi Data"""

df.isnull().sum()

df.describe()

sns.histplot(df['Outcome'], kde = True);

korelasi = df.corr()

sns.heatmap(korelasi, annot=True, cmap='coolwarm', fmt=".2f")
plt.show()

"""## Naive Bayes

### Split Data
"""

# Split data into dependent/independent variables
X = df[['Age','Pregnancies','Glucose','BloodPressure','SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction']].values
y = df.iloc[:, -1].values

X_train, X_test, y_train, y_test = train_test_split(X,y,random_state = 1, test_size = .25)

X_train.shape, X_test.shape

# Scale dataset
sc = StandardScaler ()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

classifier = GaussianNB()
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)), 1)

"""### Classification"""

print("> Akurasi Score : ",accuracy_score(y_test, y_pred),"\n")
print(f'> Classification Report: \n{classification_report (y_test, y_pred)}','\n')
print(f"> F1 Score: {f1_score(y_test, y_pred)}")

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, fmt='d', cmap='Blues', cbar=False)

"""### Visualisasi"""

# Plot Precision-Recall Curve
y_pred_proba = classifier.predict_proba(X_test)[:, 1]
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)

# Buat plot
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(recall, precision, label='Naive Bayes Classification', color='firebrick')
ax.set_title('Precision-Recall Curve')
ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
plt.box(False)
ax.legend();

# Plot ROC Curve
y_pred_proba = classifier.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_proba)

# Buat plot
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(fpr, tpr, label='Naive Bayes Classification', color='firebrick')

# Set judul dan label sumbu
ax.set_title('ROC Curve')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
plt.box(False)

# Tambahkan legenda
ax.legend();

"""## PSO

> Deskripsi :  
1. Parameter masalah:
- Banyaknya dimensi ( d ) = 3
- Batas bawah ( minx ) = -10.0
- Batas atas ( maxx ) = 10.0
2. Hyperparameter dari algoritma:  
- Jumlah partikel ( N ) = 50
- Jumlah iterasi maksimum ( max_iter ) = 100
- koefisien inersia ( w ) = 0,729
- koefisien kognitif ( c1 ) = 1,49445
- koefisien sosial ( c2 ) = 1,49445
3. Inputs
- Fungsi kebugaran
- Parameter masalah (disebutkan di atas)
- Ukuran populasi ( N ) dan Jumlah iterasi maksimum ( max_iter )
- Algoritma Parameter hiper spesifik ( w , c1 , c2 )
"""

# Fungsi fitness untuk Naive Bayes dengan data diabetes
def fitness_naive_bayes(position):
    # Menggunakan position sebagai hyperparameter untuk Naive Bayes
    # Contoh: position = [smoothing_param]

    # Batasan untuk var_smoothing
    smoothing_param = max(0.0, position[0])  # Menggunakan nilai maksimum antara 0 dan nilai position[0]

    clf = GaussianNB(var_smoothing=smoothing_param)
    scores = cross_val_score(clf, X, y, cv=5)
    fitness_val = -scores.mean()  # Menggunakan negatif mean cross-val score sebagai fitness
    return fitness_val


# Kelas Partikel
class Particle:
    def __init__(self, fitness, dim, minx, maxx, seed):
        self.rnd = random.Random(seed)
        self.position = [0.0 for i in range(dim)]
        self.velocity = [0.0 for i in range(dim)]
        self.best_part_pos = [0.0 for i in range(dim)]

        for i in range(dim):
            self.position[i] = ((maxx[i] - minx[i]) * self.rnd.random() + minx[i])
            self.velocity[i] = ((maxx[i] - minx[i]) * self.rnd.random() + minx[i])

        self.fitness = fitness(self.position)
        self.best_part_pos = copy.copy(self.position)
        self.best_part_fitnessVal = self.fitness

# Fungsi PSO
def pso(fitness, max_iter, n, dim, minx, maxx):
    w = 0.729
    c1 = 1.49445
    c2 = 1.49445

    rnd = random.Random(0)

    swarm = [Particle(fitness, dim, minx, maxx, i) for i in range(n)]

    best_swarm_pos = [0.0 for i in range(dim)]
    best_swarm_fitnessVal = sys.float_info.max

    for i in range(n):
        if swarm[i].fitness < best_swarm_fitnessVal:
            best_swarm_fitnessVal = swarm[i].fitness
            best_swarm_pos = copy.copy(swarm[i].position)

    Iter = 0
    while Iter < max_iter:
        if Iter % 10 == 0 and Iter > 1:
            print("Iter = " + str(Iter) + " best fitness = %.3f" % best_swarm_fitnessVal)

        for i in range(n):
            for k in range(dim):
                r1 = rnd.random()
                r2 = rnd.random()

                swarm[i].velocity[k] = (w * swarm[i].velocity[k]) + (c1 * r1 * (swarm[i].best_part_pos[k] - swarm[i].position[k])) + (c2 * r2 * (best_swarm_pos[k] - swarm[i].position[k]))

                if swarm[i].velocity[k] < minx[k]:
                    swarm[i].velocity[k] = minx[k]
                elif swarm[i].velocity[k] > maxx[k]:
                    swarm[i].velocity[k] = maxx[k]

            for k in range(dim):
                swarm[i].position[k] += swarm[i].velocity[k]

            swarm[i].fitness = fitness(swarm[i].position)

            if swarm[i].fitness < swarm[i].best_part_fitnessVal:
                swarm[i].best_part_fitnessVal = swarm[i].fitness
                swarm[i].best_part_pos = copy.copy(swarm[i].position)

            if swarm[i].fitness < best_swarm_fitnessVal:
                best_swarm_fitnessVal = swarm[i].fitness
                best_swarm_pos = copy.copy(swarm[i].position)

        Iter += 1

    return best_swarm_pos

# Tentukan jumlah dimensi (fitur) dan rentang nilai minimum dan maksimum untuk setiap dimensi
dim = X_train.shape[1]
minx = [-10.0 for i in range(dim)]
maxx = [10.0 for i in range(dim)]

# Fungsi fitness yang ingin dioptimalkan adalah fitness_naive_bayes
fitness = fitness_naive_bayes

# Parameter PSO
num_particles = 50
max_iter = 100

# Jalankan PSO
best_position = pso(fitness, max_iter, num_particles, dim, minx, maxx)

print("\nPSO completed\n")
print("\nBest solution found:")
print(["%.6f"%best_position[k] for k in range(dim)])
fitnessVal = fitness(best_position)
print("fitness of best solution = %.6f" % fitnessVal)

print("\nEnd particle swarm for Naive Bayes\n")

"""## Kesimpulan

> Nilai fitness terbaik yang ditemukan oleh algoritma Particle Swarm Optimization (PSO) adalah -0.751337. Nilai fitness ini merupakan nilai negatif dari rata-rata skor validasi silang (cross-validation score) yang diperoleh dari model Naive Bayes Gaussian dengan menggunakan nilai hyperparameter var_smoothing yang optimal.

> Skor validasi silang adalah metrik evaluasi yang digunakan untuk menilai performa model pada data yang belum pernah dilihat sebelumnya. Semakin tinggi skor validasi silang, semakin baik generalisasi model pada data baru.

> Nilai fitness -0.751337 yang ditemukan oleh algoritma PSO mengindikasikan bahwa model Naive Bayes Gaussian dengan nilai hyperparameter var_smoothing yang optimal memiliki rata-rata skor validasi silang sebesar 0.751337 atau sekitar 75.13% pada dataset diabetes yang digunakan.
Skor validasi silang 75.13% dapat dianggap cukup baik untuk sebuah model klasifikasi pada dataset diabetes ini, tetapi masih ada ruang untuk perbaikan lebih lanjut.

> Jadi, nilai fitness -0.751337 menunjukkan bahwa model Naive Bayes Gaussian dengan hyperparameter var_smoothing yang optimal memiliki kemampuan generalisasi yang cukup baik pada dataset diabetes yang digunakan dalam eksperimen ini.
"""