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

def no_post_hoc_method_with_dataframe(model, dataloader):
    df_test = get_split_dataframe(model, dataloader, 'test')
    predicted = df_test['predicted'].to_numpy()
    num_tests = len(df_test)
    
    return predicted, df_test, num_tests

def mc_dropout(model, dataloader, num_samples, n_classes, no_post_hoc_method_results, threshold_halting_criterion, max_forward_passes=1000, num_threads=4):
    def enable_training_dropout(model):
        for m in model.modules():
            if isinstance(m, nn.Dropout):
                m.train()

    if no_post_hoc_method_results is None:
        return None, None

    if not threshold_halting_criterion:
        threshold_halting_criterion = 0.001
    dropout_predictions = np.empty((0, num_samples, n_classes))
    lock = Lock()
    
    unique_classes = sorted(set(no_post_hoc_method_results))
    class_to_index = {cls: idx for idx, cls in enumerate(unique_classes)}

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
                    break

    mean_predictions = np.mean(dropout_predictions, axis=0)
    
    target_class_values = np.array([mean_predictions[i, class_to_index[target_class]] for i, target_class in enumerate(no_post_hoc_method_results)])
    
    final_predictions = np.argmax(mean_predictions, axis=1)
    
    return target_class_values, final_predictions

def trustscore(model, dataloader, reference_df, distance, k_nearest):
    class TrustScore:
        def __init__(self, reference_data, correct_class, distance, k_nearest):
            self.reference_data = list(reference_data)
            self.correct_class = list(correct_class)
            
            self.alpha_reference_data = list(reference_data)
            self.alpha_correct_class = list(correct_class)
            
            self.number_class = len(set(correct_class))
            self.indices_class = list(set(correct_class))
            self.elements_class = [self.correct_class.count(val) for val in self.indices_class] 
            
            self.distance = distance
            
            if self.distance=="k-nearest":
                self.k_nearest = int(k_nearest)
            else:
                self.k_nearest = None
            


        def TrustScore(self, feature_prediction, class_prediction=None):
            
            feature_prediction = list(feature_prediction)
            
            if class_prediction!=None:
                predicted_score = fun_TrustScore(self.alpha_reference_data, self.alpha_correct_class, feature_prediction, class_prediction, self.distance, self.k_nearest)
            else:
                predicted_score = {}
                for val_class in self.indices_class:
                    predicted_score[val_class] = fun_TrustScore(self.alpha_reference_data, self.alpha_correct_class, feature_prediction, val_class, self.distance, self.k_nearest)
                    
            return predicted_score


    def fun_TrustScore(alpha_reference_data, alpha_correct_class, feature_prediction, class_prediction, distance, k_nearest):
        
        class_type = list(set(alpha_correct_class))
        number_class = len(set(alpha_correct_class))
        
        list_h_set = []
        
        for i_class in range(0, number_class):
            list_h_set.append([])
            for i, val in enumerate(alpha_correct_class):
                if val == class_type[i_class]:
                    list_h_set[i_class].append(list(alpha_reference_data[i]))
        
        dist_h_set = []
        
        if distance == "nearest":
            for i_class in range(0, number_class):
                dist_h_set.append(fun_distance_nearest(list_h_set[i_class], feature_prediction))
        elif distance == "average":
            for i_class in range(0, number_class):
                dist_h_set.append(fun_distance_average(list_h_set[i_class], feature_prediction))    
        elif distance == "centroid": 
            for i_class in range(0, number_class):
                dist_h_set.append(fun_distance_centroid(list_h_set[i_class], feature_prediction)) 
        elif distance == "k-nearest":
            for i_class in range(0, number_class):
                dist_h_set.append(fun_distance_k_nearest(list_h_set[i_class], feature_prediction, k_nearest))         
        
        try:
            predicted_class_index = class_type.index(class_prediction)
        except ValueError:
            return float(0.0)
        
        distance_coincident = dist_h_set[predicted_class_index]
        
        dist_h_set.pop(predicted_class_index)
        
        if not dist_h_set: 
            return float(0.0)
            
        distance_not_coincident = min(dist_h_set)
        
        epsilon = np.finfo(float).eps 
        trust_score = distance_not_coincident / (distance_coincident + epsilon)
        
        return float(trust_score)
    
    def fun_distance_nearest(reference_set, x_test):
        
        if not reference_set:
            return np.nan
        
        distances_list = []
        
        for i_temp, val in enumerate(reference_set):
            distances_list.append(0)
            for j_temp, val_feature in enumerate(val):
                distances_list[i_temp] += (val_feature - x_test[j_temp])**2
            
            distances_list[i_temp] = np.sqrt(distances_list[i_temp])
        
        return min(distances_list)
        
    def fun_distance_k_nearest(reference_set, x_test, k):
        
        distances_list = []
        
        for i_temp, val in enumerate(reference_set):
            distances_list.append(0)
            for j_temp, val_feature in enumerate(val):
                distances_list[i_temp] += (val_feature-x_test[j_temp])**2
            
            distances_list[i_temp] = np.sqrt(distances_list[i_temp])    

        
        k_distances_list= []
        for i in range(0,k):
            k_distances_list.append(min(distances_list))
            distances_list.pop(np.argmin(distances_list))

        return np.mean(k_distances_list)  


    def fun_distance_average(reference_set,x_test):
        
        distances_list = []
        
        for i_temp, val in enumerate(reference_set):
            distances_list.append(0)
            for j_temp, val_feature in enumerate(val):
                distances_list[i_temp] += (val_feature-x_test[j_temp])**2
            
            distances_list[i_temp] = np.sqrt(distances_list[i_temp])    

        return np.mean(distances_list)


    def fun_distance_centroid(reference_set, x_test):
        
        centroid_features = []
        
        n_features = len(x_test)
        
        for i_features in range(0, n_features):
            centroid_features.append(0)
            
            i_ref = -1
            for i_ref, val in enumerate(reference_set):
                centroid_features[i_features] += val[i_features]
            
            centroid_features[i_features] = centroid_features[i_features]/(i_ref+1)
            
        centroid_distance = 0
        for j_temp, val_feature in enumerate(centroid_features):
                centroid_distance += (val_feature-x_test[j_temp])**2
        centroid_distance = np.sqrt(centroid_distance)

        return centroid_distance  
    

    df_training = get_split_dataframe(model, dataloader, 'training')
        
    TrustScore_instance = TrustScore(df_training.drop(columns=['GT', 'predicted']).values, reference_df['GT'].values, distance, k_nearest)

    trust_scores = []
    for i in range(len(reference_df)):
        feature_prediction = reference_df.drop(columns=['GT', 'predicted']).iloc[i].values
        trust_score = TrustScore_instance.TrustScore(feature_prediction, reference_df['predicted'].iloc[i])
        trust_scores.append(trust_score)
        
    return np.array(trust_scores)
        
    

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

def get_fc_output(model, x):
    for _, module in model.named_modules():
        if isinstance(module, th.nn.Linear):
            return module(x)
    return None

def calculate_results_row(gt_value, predicted, fc_output):
    row = {
        'GT': gt_value.item(),
        'predicted': predicted
    }
    
    fc_output_values = fc_output.squeeze().tolist()
    for i, value in enumerate(fc_output_values):
        row[f'node_{i}'] = value
    
    return row

def process_batch(model, feature, gt_value):
    feature = feature.unsqueeze(0)
    feature_flat = feature.view(feature.size(0), -1)
    
    fc_output = get_fc_output(model, feature_flat)
    if fc_output is not None:
        final_output = model(feature_flat)
        predicted = th.argmax(final_output, dim=1).item()
        
        return calculate_results_row(gt_value, predicted, fc_output)
    return None

def get_split_dataframe(model, dataloader, target_split):
    model.eval()
    results = []
    
    with th.no_grad():
        for batch_features, gt, split in dataloader:
            for feature, gt_value, split_value in zip(batch_features, gt, split):
                if split_value == target_split:
                    row = process_batch(model, feature, gt_value)
                    if row is not None:
                        results.append(row)
    
    return pd.DataFrame(results)

def get_all_dataframes(model, dataloader):
    df_training = get_split_dataframe(model, dataloader, 'training')
    df_test = get_split_dataframe(model, dataloader, 'test')
    return df_training, df_test