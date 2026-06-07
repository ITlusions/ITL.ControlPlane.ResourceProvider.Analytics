# User Scenario: Building & Running Notebooks on Analytics Provider

##  **User Profile**

**Name:** Alice Chen  
**Role:** Data Scientist  
**Goal:** Build a machine learning model using Jupyter notebooks with GPU-accelerated Spark  
**Environment:** Azure subscription `prod-ml-analytics`, resource group `data-science-team`

---

##  **User Workflow**

### **Phase 1: Create Notebook Environment**

#### Step 1: User Discovers the API

Alice finds the Analytics Provider API documentation:
```
https://notebooks.analytics.itl.com/api/docs
```

She learns that she can create notebooks via REST API or CLI.

#### Step 2: Create Notebook via CLI or API

**Option A: Using CLI (if available)**
```bash
az analytics notebook create \
  --subscription prod-ml-analytics \
  --resource-group data-science-team \
  --name "fraud-detection-v1" \
  --location eastus \
  --kernel python3.11 \
  --compute-sku Standard_D8s_v3 \
  --memory 32 \
  --cpu 8 \
  --storage 200
```

**Option B: Direct API Call**
```bash
curl -X POST https://api.analytics.itl.com/subscriptions/prod-ml-analytics/resourceGroups/data-science-team/providers/ITL.Analytics/notebooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fraud-detection-v1",
    "location": "eastus",
    "properties": {
      "kernel": "python3.11",
      "computeSku": "Standard_D8s_v3",
      "memory_gb": 32,
      "cpu_cores": 8,
      "storage_gb": 200
    }
  }'
```

#### Step 3: Provider Processes Request

**What happens behind the scenes:**

```
Analytics Provider receives POST request
  
Validates input (name, location, resources)
  
Creates database record (status: Creating)
  
Calls Container Provider
   Request: Create pod with:
     Image: jupyter/base-notebook:latest
     Resources: 8 CPU, 32GB RAM, 200GB storage
     Port: 8888 (Jupyter)
     Labels: notebook-id=..., owner=alice.chen
  
   Response: Pod created, status=Pending
      
      Waits for pod to be Running (polls every 5s, timeout 5min)
       Status updates: Pending  Running
       Gets pod IP: 10.0.1.42:8888
          
          Creates MinIO bucket: analytics-550e8400-e29b...
           Sets CORS for web access
           Sets policies for notebook access
           Returns bucket path: s3://analytics-550e8400.../
              
              Updates database record (status: Running)
               Stores: pod_name, pod_ip, storage_bucket, notebook_url
```

#### Step 4: User Receives Notebook URL

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "fraud-detection-v1",
  "location": "eastus",
  "status": "Running",
  "owner_id": "alice.chen",
  "created_at": "2026-06-07T10:30:00Z",
  "updated_at": "2026-06-07T10:35:00Z",
  "properties": {
    "kernel": "python3.11",
    "computeSku": "Standard_D8s_v3",
    "memory_gb": 32,
    "cpu_cores": 8,
    "storage_gb": 200,
    "pod_name": "notebook-550e8400-e29b-41d4-a716-446655440000",
    "storage_bucket": "analytics-550e8400-e29b-41d4",
    "notebook_url": "https://notebooks.analytics.itl.com/550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**CLI Response:**
```
 Notebook created successfully!

Notebook ID:  550e8400-e29b-41d4-a716-446655440000
Name:         fraud-detection-v1
Status:       Running
URL:          https://notebooks.analytics.itl.com/550e8400-e29b-41d4-a716-446655440000

Access your notebook: https://notebooks.analytics.itl.com/550e8400-e29b-41d4-a716-446655440000
```

---

### **Phase 2: Access & Build Notebook**

#### Step 5: Alice Opens Notebook in Browser

Alice clicks the notebook URL:
```
https://notebooks.analytics.itl.com/550e8400-e29b-41d4-a716-446655440000
```

**What she sees:**

```
 JupyterLab Interface 
                                                              
   File Browser      fraud-detection-v1.ipynb            
   .local                                                  
   work/            In [1]:                                
   data/            # Fraud Detection Model                
   notebooks/       # Using Spark + XGBoost               
                                                             
                      import pandas as pd                    
                      import numpy as np                     
                      from pyspark.sql import SparkSession   
                                                             
                      # Initialize Spark                     
                      spark = SparkSession.builder \         
                          .appName("fraud-detection") \      
                          .getOrCreate()                     
                                                             
                      print("Spark version:", spark.version) 
                      print("CPUs available:", ...) 
                                                             
                      In [2]:                                
                                                             


Hardware displayed:
 Resources 
 CPU: 8 cores                     
 Memory: 32 GB                    
 Storage: 200 GB                  
 Kernel: python3.11               

```

#### Step 6: Alice Writes Code

She creates multiple cells to build her model:

**Cell 1: Setup & Load Data**
```python
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
import xgboost as xgb

# Initialize Spark
spark = SparkSession.builder \
    .appName("fraud-detection") \
    .master("local[8]") \
    .getOrCreate()

print(f"Spark version: {spark.version}")
print(f"CPUs available: 8")
print(f"Memory available: 32GB")

# Load data from S3
df = spark.read.parquet("s3://data-lake/transactions/*.parquet")
print(f"Loaded {df.count()} records")
```

**Cell 2: Data Exploration**
```python
# Check schema
df.printSchema()

# Basic statistics
df.describe().show()

# Check for missing values
from pyspark.sql.functions import col, sum as spark_sum
df.select([spark_sum(col(c).isNull().cast("int")).alias(c) 
           for c in df.columns]).show()
```

**Cell 3: Feature Engineering**
```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.preprocessing import StandardScaler

# Select features
features = ['amount', 'hours', 'merchant_score', 'user_history']
assembler = VectorAssembler(inputCols=features, outputCol="features_raw")

# Transform data
df_features = assembler.transform(df)

# Scale features
scaler = StandardScaler(inputCol="features_raw", outputCol="features")
df_final = scaler.fit(df_features).transform(df_features)

print(f"Features ready: {df_final.count()} records")
```

**Cell 4: Train Model**
```python
from pyspark.ml.classification import GBTClassifier

# Initialize model
gbt = GBTClassifier(
    labelCol="is_fraud",
    featuresCol="features",
    maxIter=100,
    maxDepth=5,
    seed=42
)

# Train
print("Training model...")
model = gbt.fit(df_final)
print(" Model trained successfully")

# Get feature importance
importance = model.featureImportances.toArray()
for i, feat in enumerate(features):
    print(f"{feat}: {importance[i]:.4f}")
```

**Cell 5: Evaluate Model**
```python
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# Make predictions
predictions = model.transform(df_final)

# Evaluate
evaluator = BinaryClassificationEvaluator(
    labelCol="is_fraud",
    metricName="areaUnderROC"
)

auc = evaluator.evaluate(predictions)
print(f"AUC-ROC: {auc:.4f}")

# Additional metrics
predictions_rdd = predictions.select("prediction", "is_fraud").rdd
metrics = BinaryClassificationMetrics(predictions_rdd)
print(f"Precision: {metrics.precisionByThreshold().collect()}")
print(f"Recall: {metrics.recallByThreshold().collect()}")
```

---

### **Phase 3: Execute & Monitor**

#### Step 7: Alice Runs Cells

She clicks "Run All" or runs cells individually.

**What she sees in real-time:**

```
Cell 1: Setup & Load Data
 [Kernel busy] 
 Executing...                                
 [] 3s     


OUTPUT:
Spark version: 3.5.0
CPUs available: 8
Memory available: 32GB
Loaded 1,245,632 records
```

**Cell 2: Data Exploration**
```
OUTPUT:
root
 |-- transaction_id: string
 |-- amount: double
 |-- currency: string
 |-- hours: integer
 |-- merchant_score: double
 |-- user_history: double
 |-- is_fraud: integer

+------+-----+-----+-----+-----+-----+
|amount|hours|count|mean |min  |max  |
+------+-----+-----+-----+-----+-----+
|100   |12   |5234 |2.15 |0.1  |8.9  |
+------+-----+-----+-----+-----+-----+

Missing values check:
transaction_id: 0
amount: 0
is_fraud: 0
```

**Cell 3: Feature Engineering**
```
 [Kernel busy] 
 Transforming data...                        
 [] 15s      


OUTPUT:
Features ready: 1,245,632 records
```

**Cell 4: Train Model (THIS ONE TAKES TIME)**
```
 [Kernel busy] 
 Training model...                                       
 Iteration 1/100: [] 12%    
 Iteration 2/100: [] 24%    
 ...                                                     
 Iteration 100/100: [] 100%   
                                                        
 Total time: 2 min 45 sec                              


OUTPUT:
 Model trained successfully

Feature Importance:
user_history: 0.3421
amount: 0.2156
merchant_score: 0.2034
hours: 0.2389
```

**Cell 5: Evaluate Model**
```
 [Kernel busy] 
 Evaluating model...                         
 [] 8s             


OUTPUT:
AUC-ROC: 0.9524

Precision: [0.95, 0.92, 0.87, 0.81]
Recall: [0.88, 0.91, 0.94, 0.97]
```

---

### **Phase 4: Save & Deploy**

#### Step 8: Save Model & Results

Alice adds final cells to save her work:

```python
# Save model
model.save("s3://models/fraud-detection/v1")
print(" Model saved to S3")

# Save metrics
metrics_df = pd.DataFrame({
    'metric': ['AUC-ROC', 'Precision', 'Recall', 'F1-Score'],
    'value': [0.9524, 0.92, 0.91, 0.915]
})

metrics_df.to_csv("s3://models/fraud-detection/v1/metrics.csv")
print(" Metrics saved")

# Save notebook automatically
# (JupyterLab auto-saves every 30 seconds)
```

#### Step 9: Persist Notebook

**What happens:**
```
Notebook cells saved to:
  s3://analytics-550e8400-e29b-41d4/fraud-detection-v1.ipynb
  
Execution history saved to:
  s3://analytics-550e8400-e29b-41d4/execution-log.json

Assets saved to:
  s3://analytics-550e8400-e29b-41d4/plots/
  s3://analytics-550e8400-e29b-41d4/data/
```

#### Step 10: Alice Stops Notebook (Optional)

When done, she can stop or delete the notebook:

```bash
# List notebooks
az analytics notebook list \
  --subscription prod-ml-analytics \
  --resource-group data-science-team

# Output:
# ID                     Name                    Status    Created
# 550e8400-e29b-41d4...  fraud-detection-v1     Running   2026-06-07 10:30

# Stop notebook (keeps data)
az analytics notebook stop \
  --id 550e8400-e29b-41d4-a716-446655440000

# Delete notebook (removes pod + storage)
az analytics notebook delete \
  --id 550e8400-e29b-41d4-a716-446655440000 \
  --resource-group data-science-team
```

---

##  **What Alice Sees in Each Phase**

### **Timeline View**

```
T+0s    [POST /notebooks] 
         201 Created: Notebook record created
         Status: Creating
        
T+2s    [Container Provider]
         Pod spec sent to Kubernetes
         Status: Pending
        
T+15s   [Container Provider Poll]
         Pod status: Running
         Pod IP: 10.0.1.42:8888
         Notebook reachable
        
T+20s   [MinIO Setup]
         Bucket created: analytics-550e8400...
         CORS configured
         Policies set
        
T+22s   [Database Update]
         Status: Running
         URL: https://notebooks.analytics.itl.com/550e8400-e29b...
         Response sent to Alice

T+25s   [Alice Opens Browser]
         JupyterLab loads successfully

T+25s - T+180s [Alice Works]
         Cell 1 (5s): Data loaded
         Cell 2 (8s): Explored data
         Cell 3 (15s): Features engineered
         Cell 4 (165s): Model trained [LONG RUNNING]
         Cell 5 (10s): Model evaluated

T+180s+ [Alice Saves]
         Notebook saved to S3
         Model saved
         Metrics saved
         Ready for deployment
```

---

##  **API Calls from Alice's Perspective**

### **Call 1: Create Notebook**
```
Request:
  POST /subscriptions/prod-ml-analytics/resourceGroups/data-science-team/providers/ITL.Analytics/notebooks
  Body: { name, location, properties }
  
Wait Time: ~22 seconds

Response:
  201 Created
  { id, name, status: "Running", notebook_url, ... }
```

### **Call 2: List My Notebooks**
```
Request:
  GET /subscriptions/prod-ml-analytics/resourceGroups/data-science-team/providers/ITL.Analytics/notebooks

Response:
  200 OK
  { value: [ notebook1, notebook2, ... ] }
```

### **Call 3: Get Notebook Details**
```
Request:
  GET /subscriptions/prod-ml-analytics/resourceGroups/data-science-team/providers/ITL.Analytics/notebooks/550e8400...

Response:
  200 OK
  { id, name, status, properties, pod_name, storage_bucket, notebook_url }
```

### **Call 4: Delete Notebook**
```
Request:
  DELETE /subscriptions/prod-ml-analytics/resourceGroups/data-science-team/providers/ITL.Analytics/notebooks/550e8400...

Wait Time: ~10 seconds (cleanup)

Response:
  204 No Content
  (Pod deleted, bucket deleted, database record removed)
```

---

##  **Monitoring & Observability**

### **What Alice Can See**

**In Notebook Logs:**
```
2026-06-07 10:30:00 [INFO] Notebook session started
2026-06-07 10:30:15 [INFO] Connected to Spark cluster
2026-06-07 10:30:20 [INFO] MinIO bucket mounted at /mnt/s3
2026-06-07 10:32:45 [INFO] Model training started
2026-06-07 10:35:50 [INFO] Model training completed (AUC=0.9524)
2026-06-07 10:36:00 [INFO] Results saved to S3
```

**In Analytics Provider Logs:**
```
2026-06-07 10:30:00 [INFO] create_notebook: subscription=prod-ml-analytics, name=fraud-detection-v1
2026-06-07 10:30:01 [INFO] Calling Container Provider to create pod
2026-06-07 10:30:05 [INFO] Pod created: notebook-550e8400-e29b-41d4-a716-446655440000
2026-06-07 10:30:10 [INFO] Waiting for pod to be Running...
2026-06-07 10:30:20 [INFO] Pod status: Running (IP: 10.0.1.42:8888)
2026-06-07 10:30:21 [INFO] Creating MinIO bucket: analytics-550e8400-e29b-41d4
2026-06-07 10:30:22 [INFO] Notebook status updated to Running
2026-06-07 10:30:22 [INFO] Returning notebook URL to client
```

**Resource Usage During Execution:**
```
Cell 4 (Model Training):
   CPU: 7.8/8 cores (97%)
   Memory: 28.5/32 GB (89%)
   Disk I/O: 450 MB/s (reading training data)
   Duration: 165 seconds
```

---

##  **User Experience Highlights**

### **What Alice Loves**
 **One-click setup** - No infrastructure management  
 **Instant access** - URL ready in ~22 seconds  
 **Auto-persistence** - Notebooks saved to S3  
 **Resource control** - Specify exact CPU/memory/storage  
 **Pay-per-use** - Only charged while notebook runs  
 **Team access** - Share notebooks via resource group  

### **What Frustrates Her (Future Improvements)**
 Can't see pod startup progress in real-time  
 No GPU selection yet (Phase 2 will add this)  
 Can't connect to existing Spark clusters  
 Limited to local Spark (Phase 2 adds distributed)  

---

##  **End State**

Alice has:
-  Created a notebook environment with 1 command
-  Written and tested ML model code
-  Trained a model (165 seconds of computation)
-  Evaluated results (AUC = 0.9524)
-  Saved model + metrics to S3
-  Persisted entire notebook to cloud storage
-  Ready to share or deploy

**Total time: ~5 minutes (mostly waiting for model training)**

---

##  **Next: Phase 2**

When Phase 2 (Spark Clusters) is ready, Alice will:
1. Create Spark cluster with GPU workers
2. Submit notebooks as jobs
3. Scale to distributed training
4. Monitor cross-cluster execution
5. Auto-save results and artifacts

