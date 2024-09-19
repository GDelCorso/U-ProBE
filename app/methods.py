import numpy as np
import torch as th
import torch.nn as nn
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

def trustscore(model, dataloader, num_samples):
    # Implementazione del metodo Trustscore
    # Per ora, ritorniamo valori casuali
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