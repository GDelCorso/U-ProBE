import numpy as np
import torch as th
import torch.nn as nn
import pandas as pd
import concurrent.futures
from threading import Lock

def no_post_hoc_method(model, dataloader):
    model.eval()
    inference_results = []
    
    with th.no_grad():
        for batch_features, _, split in dataloader:
            for feature, split_value in zip(batch_features, split):
                if split_value == 'test': 
                    outputs = model(feature.unsqueeze(0)) 
                    inference_results.extend(np.argmax(outputs, axis=1).cpu().numpy())
                    
    return np.array(inference_results)

def mc_dropout(model, dataloader, num_samples, n_classes, threshold_halting_criterion, max_forward_passes=1000, num_threads=4):
    def enable_training_dropout(model):
        for m in model.modules():
            if isinstance(m, nn.Dropout):
                m.train()


    if not threshold_halting_criterion:
        threshold_halting_criterion = 0.001
    dropout_predictions = np.empty((0, num_samples, n_classes))
    lock = Lock()

    def process_forward_pass():
        predictions = np.empty((0, n_classes))
        model.eval()
        enable_training_dropout(model)
        
        softmax = nn.Softmax(dim=1)
        
        with th.no_grad():
            for images, _, splits in dataloader:
                test_indices = [i for i, split in enumerate(splits) if split == 'test']
                test_images = [images[i] for i in test_indices]
                
                if not test_images:
                    continue 
                
                test_images_tensor = th.stack(test_images)
                
                outputs = model(test_images_tensor)
                outputs = softmax(outputs)
                
                predictions = np.vstack((predictions, outputs.cpu().numpy()))
        
        return predictions

    def calculate_halting_criterion(predictions):
        means = np.mean(predictions, axis=0)
        variance_of_means = np.var(means, axis=0)
        return np.median(variance_of_means) / len(predictions)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for fp in range(max_forward_passes):
            future = executor.submit(process_forward_pass,)
            new_predictions = future.result()
            
            with lock:
                dropout_predictions = np.vstack((dropout_predictions, [new_predictions]))
            
            if fp > 1 and fp % 5 == 0: 
                halting_criterion = calculate_halting_criterion(dropout_predictions)
                if halting_criterion < threshold_halting_criterion:
                    print(f"Early stopping at forward pass {fp + 1}")
                    break

    mean_predictions = np.mean(dropout_predictions, axis=0)
    final_predictions = np.argmax(mean_predictions, axis=1)
    return final_predictions


# Funzione per generare il DataFrame con i risultati
def get_dataframe(model, dataloader):
    model.eval()
    results = []
    
    # Funzione per calcolare la tabella dei risultati
    def calculate_results_table(gt_value, predicted, fc_output):
        row = {
            'GT': gt_value.item(),
            'predicted': predicted
        }
        
        # Aggiungi i valori dei nodi del layer fully connected
        fc_output_values = fc_output.squeeze().tolist()
        for i, value in enumerate(fc_output_values):
            row[f'node_{i}'] = value
        return row

    # Funzione per ottenere l'output del primo layer fully connected
    def get_fc_output(model, x):
        for _, module in model.named_modules():
            if isinstance(module, th.nn.Linear):
                return module(x)
        return None
    
    with th.no_grad():
        for batch_features, gt, split in dataloader:
            for feature, gt_value, split_value in zip(batch_features, gt, split):
                if split_value == 'training':
                    feature = feature.unsqueeze(0)
                    
                    # Appiattisci l'immagine
                    feature_flat = feature.view(feature.size(0), -1)  

                    # Ottieni l'output del fully connected
                    fc_output = get_fc_output(model, feature_flat)
                    if fc_output is not None:
                        # Ottieni l'output finale del modello
                        final_output = model(feature_flat)
                        predicted = th.argmax(final_output, dim=1).item()
                        
                        # Usa la funzione esterna per calcolare la riga della tabella
                        row = calculate_results_table(gt_value, predicted, fc_output)
                        results.append(row)
                    else:
                        break
    
    # Crea un DataFrame con i risultati
    df = pd.DataFrame(results)
    return df

# Funzione trustscore ridotta
def trustscore(model, dataloader, num_samples):
    df = get_dataframe(model, dataloader)
    return np.random.randint(0, 10, num_samples)

def topological_data_analysis(model, dataloader, num_samples):
    # Implementazione dell'analisi topologica dei dati
    # Per ora, ritorniamo valori casuali
    return np.random.randint(0, 10, num_samples)

def ensemble(model, dataloader, num_samples):
    # Implementazione del metodo Ensemble
    # Per ora, ritorniamo valori casuali
    return np.random.randint(0, 10, num_samples)

def few_shot_learning(model, dataloader, num_samples):
    # Implementazione del Few Shot Learning
    # Per ora, ritorniamo valori casuali
    return np.random.randint(0, 10, num_samples)