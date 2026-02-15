from app import create_app
from app.prediction.predictor import EnergyPredictor

def train_prediction_model():
    """Standalone script to train the ML model"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("⚡ VOLTONIC - ML Model Training")
        print("="*60 + "\n")
        
        predictor = EnergyPredictor()
        
        # Train model (using last 7 days of data)
        success, result = predictor.train_model(hours_back=168)
        
        if success:
            print("\n✅ Training completed successfully!")
            print(f"📈 MAE: {result['mae']} kW")
            print(f"📈 R² Score: {result['r2_score']}")
            print(f"📊 Training samples: {result['training_samples']}")
            print(f"📊 Test samples: {result['test_samples']}")
            
            # Get feature importance
            importance, _ = predictor.get_feature_importance()
            if importance:
                print("\n🎯 Feature Importance:")
                for feat in importance:
                    print(f"  • {feat['feature']}: {feat['importance']:.4f}")
            
            # Test prediction
            print("\n🔮 Testing prediction...")
            prediction, error = predictor.predict_next_hour()
            if prediction:
                print(f"✅ Next hour predicted load: {prediction['predicted_load_kw']} kW")
                print(f"📍 Confidence interval: [{prediction['confidence_interval']['lower']}, {prediction['confidence_interval']['upper']}] kW")
            else:
                print(f"❌ Prediction failed: {error}")
        else:
            print(f"\n❌ Training failed: {result}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    train_prediction_model()