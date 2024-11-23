import os
import csv

# Leggere i path dal CSV e ottenere i nomi dei file
filenames = set()
with open('C:/Users/Huawei/Desktop/Tirocinio CNR/U-proBE/GUI/example/csv_mnist_mini.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        image_path = row['image_path']
        filename = os.path.basename(image_path)
        filenames.add(filename)

# Definire le cartelle target
target_folders = [
    'C:/Users/Huawei/Desktop/Tirocinio CNR/U-proBE/GUI/example/png/test/',
    'C:/Users/Huawei/Desktop/Tirocinio CNR/U-proBE/GUI/example/png/training/'
]

# Scorrere i file nelle cartelle target e eliminare quelli non inclusi nel CSV
for folder in target_folders:
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file not in filenames:
                file_path = os.path.join(root, file)
                os.remove(file_path)
