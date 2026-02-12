from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.conf import settings
import joblib
import pandas as pd
import os

try:
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'main/models/fraud_model.pkl')
    COLUMNS_PATH = os.path.join(settings.BASE_DIR, 'main/models/model_columns.pkl')
    
    model = joblib.load(MODEL_PATH)
    model_columns = joblib.load(COLUMNS_PATH)
except Exception as e:
    print(f"⚠️ ERROR LOADING MODEL: {e}")
    model = None
    model_columns = None

class PredictFraud(APIView):
    def post(self, request):
        if not model:
            return Response({"error": "Model not loaded"}, status=500)
            
        try:
            data = request.data
            df = pd.DataFrame([data])
            df = df.reindex(columns=model_columns, fill_value=0)
            
            prediction = model.predict(df)[0]
            probability = model.predict_proba(df)[0][1]

            return Response({
                "status": "success",
                "is_fraud": int(prediction),
                "fraud_probability": round(float(probability), 4)
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

def dashboard_view(request):
    result = None
    
    if request.method == 'POST':
        try:
            
            amount = float(request.POST.get('amount', 0))
            oldbalanceOrg = float(request.POST.get('oldbalanceOrg', 0))
            newbalanceOrig = float(request.POST.get('newbalanceOrig', 0)) 
            type_val = request.POST.get('type')

            input_data = {
                'step': 1, 'amount': amount,
                'oldbalanceOrg': oldbalanceOrg, 'newbalanceOrig': newbalanceOrig,
                'oldbalanceDest': 0.0, 'newbalanceDest': 0.0,
                'nameOrig': 'Unknown', 'nameDest': 'Unknown'
            }
            df = pd.DataFrame([input_data])
            
            if type_val in model_columns:
                df[type_val] = 1
            df = df.reindex(columns=model_columns, fill_value=0)

            if model:
                prediction = model.predict(df)[0]
                probability = model.predict_proba(df)[0][1]
                
                result = {
                    'is_fraud': prediction == 1,
                    'probability': round(probability * 100, 2),
                    'type': type_val,
                    'amount': amount,
                    'oldbalanceOrg': oldbalanceOrg, 
                    'newbalanceOrig': newbalanceOrig 
                }
        except Exception as e:
            print(f"Error: {e}")

    return render(request, 'main/dashboard.html', {'result': result})