from sklearn.cluster import KMeans, AgglomerativeClustering, AffinityPropagation
import numpy as np
import distance
import pandas as pd

def cluster (anomaly_dict, anomaly_list):
    clustered_anomalies = pd.DataFrame()
    dict_keys = list(anomaly_dict.keys())

    words = np.asarray(anomaly_list)

    lev_similarity = -1 * np.array([[distance.levenshtein(w1, w2) for w1 in words] for w2 in words])
    affprop = AffinityPropagation(affinity="precomputed", damping=0.5)
    affprop.fit(lev_similarity)

    for i in range(len(affprop.labels_)):
        current_trace = anomaly_list[i]
        current_label = affprop.labels_[i]
        current_id = dict_keys[i]

        row = pd.DataFrame([[current_id, current_trace, current_label]],
                           columns=["UNIQ_ID", "trace", "cluster_label"])
        clustered_anomalies = clustered_anomalies.append(row, ignore_index=True)

    return clustered_anomalies
