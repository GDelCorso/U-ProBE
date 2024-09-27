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


# Funzione per generare i DataFrame con i risultati
def get_dataframe(model, dataloader):
    model.eval()
    training_results = []
    test_results = []
    
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
                    
                    # Aggiungi la riga al set di risultati appropriato
                    if split_value == 'training':
                        training_results.append(row)
                    else:
                        test_results.append(row)
                else:
                    break
    
    # Crea i DataFrame con i risultati
    df_training = pd.DataFrame(training_results)
    df_test = pd.DataFrame(test_results)
    
    return df_training, df_test

# Funzione trustscore ridotta
def trustscore(model, dataloader, num_samples):
    class  TrustScore:    
        # Inizializzazione classe
        def __init__(self, reference_data, correct_class, alpha_set = 1, threshold = 1, distance="k-nearest", k_nearest = 3):
            self.reference_data = list(reference_data)
            self.correct_class = list(correct_class)
            
            self.alpha_reference_data = list(reference_data)
            self.alpha_correct_class = list(correct_class)
            
            self.number_class = len(set(correct_class))
            self.indices_class = list(set(correct_class))
            self.elements_class = [self.correct_class.count(val) for val in self.indices_class] 
            
            self.alpha_set = alpha_set
            self.threshold = threshold
            self.distance = distance
                
            self.k_nearest = int(k_nearest)


        def TrustScore(self, feature_prediction, class_prediction=None):
            
            feature_prediction = list(feature_prediction)
            
            if class_prediction!=None: 
                predicted_score = fun_TrustScore(self.alpha_reference_data, self.alpha_correct_class, \
                                                feature_prediction, class_prediction, self.distance, self.k_nearest)
            else:
                predicted_score = {}
                for val_class in self.indices_class:
                    predicted_score[val_class] = fun_TrustScore(self.alpha_reference_data, self.alpha_correct_class, \
                                                                feature_prediction, val_class, self.distance, self.k_nearest)
            return predicted_score
            
        def TrustScoreList(self, feature_prediction_list, class_prediction_list):
            predicted_score_list = []
            
            for i, feature_prediction in enumerate(feature_prediction_list):
                try:
                    predicted_score_list.append(self.TrustScore(feature_prediction, class_prediction_list[i]))
                except Exception as e:
                    predicted_score_list.append(-1)
            
            return predicted_score_list

    def fun_TrustScore(alpha_reference_data, alpha_correct_class, feature_prediction, class_prediction, distance="k-nearest", k_nearest=10):

        class_type = list(set(alpha_correct_class))
        number_class = len(set(alpha_correct_class))
        
        list_h_set = []
        
        for i_class in range(0, number_class):
            list_h_set.append([])
            for i, val in enumerate(alpha_correct_class):
                if val==class_type[i_class]:
                    list_h_set[i_class].append(list(alpha_reference_data[i]))
            
        dist_h_set = []
        
        for i_class in range(0, number_class):
            if distance=="k-nearest" :
                dist_h_set.append(fun_distance_k_nearest(list_h_set[i_class], feature_prediction, k_nearest)) 
            else:
                continue

        distance_coincident = dist_h_set[class_type.index(class_prediction)]

            
        dist_h_set.pop(class_type.index(class_prediction))
                
        distance_not_coincident = min(dist_h_set)   
        
        trust_score = distance_not_coincident/distance_coincident

        return trust_score 
    
    def fun_distance_k_nearest(reference_set, x_test, k):        
        
        # Definiamo una lista di distanze:
        distances_list = []
        
        # Scorriamo la lista delle reference:
        for i_temp, val in enumerate(reference_set):
            # Scorriamo sul numero di features e definiamo la  distanza.
            distances_list.append(0)
            for j_temp, val_feature in enumerate(val):      # val_feature è il valore di una feature del reference set i_temp-esimo (val)
                distances_list[i_temp] += (val_feature-x_test[j_temp])**2
            
            # Effettuiamo la radice:
            distances_list[i_temp] = np.sqrt(distances_list[i_temp])    

        # Warning su k:
        if k>len(reference_set):
            k = len(reference_set)
        
        
        # Si crea una lista con le k distanze più vicine:
        k_distances_list= []
        for _ in range(0,k):
            k_distances_list.append(min(distances_list))
            distances_list.pop(np.argmin(distances_list))

        return np.mean(k_distances_list)  

    df_training, df_test = get_dataframe(model, dataloader)
    
    TrustScore_instance = TrustScore(df_training.drop(columns=['GT', 'predicted']).values, df_training['GT'].values)

    trust_scores = []
    for i in range(len(df_test)):
        feature_prediction = df_test.drop(columns=['GT', 'predicted']).iloc[i].values
        trust_score = TrustScore_instance.TrustScore(feature_prediction)
        trust_scores.append(trust_score)
        
    trust_scores_max = np.array([max(score, key=score.get) for score in trust_scores])
    return trust_scores_max
        
    

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