from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

def perform_segmentation(df, n_clusters=3):
    """
    Performs clustering to identify pricing segments.
    Uses 'price', 'units_sold', 'discount_percent', 'revenue' as features.
    """
    features = ['price', 'units_sold', 'discount_percent', 'revenue']
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    df['cluster_label'] = clusters
    
    # Assign human-readable names if possible, or just return the df with clusters
    # We can perform analysis to map 0,1,2 to Low/Mid/High value if needed
    # For now, we keep the cluster IDs or map them based on average revenue
    
    cluster_summary = df.groupby('cluster_label')['revenue'].mean().sort_values()
    
    # Map clusters to descriptive names based on revenue
    cluster_map = {}
    labels = ['Low Value', 'Mid Value', 'High Value', 'Premium'] # Generic list
    
    for i, (cluster_id, _) in enumerate(cluster_summary.items()):
        if i < len(labels):
            cluster_map[cluster_id] = labels[i]
        else:
            cluster_map[cluster_id] = f"Segment {i+1}"
            
    df['segment_cluster'] = df['cluster_label'].map(cluster_map)
    
    return df, kmeans, scaler
