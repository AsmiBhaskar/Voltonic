import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.models import db, EnergyLog
from app.prediction.predictor import EnergyPredictor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import json

class PredictionTester:
    """Test suite for ML prediction model"""
    
    def __init__(self):
        self.predictor = EnergyPredictor()
        self.test_results = []
    
    def run_comprehensive_tests(self):
        """Run all test scenarios"""
        print("\n" + "="*70)
        print("🧪 VOLTONIC - ML Model Testing Suite")
        print("="*70 + "\n")
        
        # Test 1: Check data availability
        print("📊 Test 1: Data Availability Check")
        data_check = self._test_data_availability()
        print(f"✅ Result: {data_check}\n")
        
        # Test 2: Train model
        print("🤖 Test 2: Model Training")
        training_result = self._test_model_training()
        print(f"✅ Training completed: {training_result}\n")
        
        # Test 3: Feature importance
        print("🎯 Test 3: Feature Importance Analysis")
        self._test_feature_importance()
        print()
        
        # Test 4: Single prediction
        print("🔮 Test 4: Single Hour Prediction")
        self._test_single_prediction()
        print()
        
        # Test 5: Multiple hour predictions
        print("📈 Test 5: Multi-Hour Prediction Accuracy")
        self._test_rolling_predictions(hours=24)
        print()
        
        # Test 6: Peak vs Off-Peak accuracy
        print("⚡ Test 6: Peak vs Off-Peak Hour Accuracy")
        self._test_peak_vs_offpeak()
        print()
        
        # Test 7: Weekday vs Weekend accuracy
        print("📅 Test 7: Weekday vs Weekend Accuracy")
        self._test_weekday_vs_weekend()
        print()
        
        # Generate report
        self._generate_test_report()
        
        print("="*70)
        print("✅ All tests completed!")
        print("="*70 + "\n")
    
    def _test_data_availability(self):
        """Test 1: Check if sufficient data exists"""
        total_logs = EnergyLog.query.count()
        
        if total_logs == 0:
            return "❌ No data available"
        
        # Check time range
        earliest = db.session.query(db.func.min(EnergyLog.timestamp)).scalar()
        latest = db.session.query(db.func.max(EnergyLog.timestamp)).scalar()
        
        time_range = (latest - earliest).total_seconds() / 3600
        
        print(f"  • Total logs: {total_logs:,}")
        print(f"  • Time range: {earliest.strftime('%Y-%m-%d %H:%M')} to {latest.strftime('%Y-%m-%d %H:%M')}")
        print(f"  • Hours covered: {time_range:.1f}")
        
        if total_logs < 100:
            return "⚠️  Insufficient data (need at least 100 logs)"
        
        return f"✅ Sufficient data ({total_logs:,} logs, {time_range:.1f} hours)"
    
    def _test_model_training(self):
        """Test 2: Train the model"""
        success, result = self.predictor.train_model(hours_back=168)
        
        if not success:
            print(f"  ❌ Training failed: {result}")
            return False
        
        print(f"  • MAE: {result['mae']} kW")
        print(f"  • R² Score: {result['r2_score']}")
        print(f"  • Training samples: {result['training_samples']}")
        print(f"  • Test samples: {result['test_samples']}")
        
        self.test_results.append({
            'test': 'Model Training',
            'mae': result['mae'],
            'r2_score': result['r2_score']
        })
        
        return True
    
    def _test_feature_importance(self):
        """Test 3: Analyze feature importance"""
        importance, error = self.predictor.get_feature_importance()
        
        if error:
            print(f"  ❌ {error}")
            return
        
        print("  Feature Importance Ranking:")
        for i, feat in enumerate(importance, 1):
            bar = "█" * int(feat['importance'] * 50)
            print(f"  {i}. {feat['feature']:<20} {bar} {feat['importance']:.4f}")
    
    def _test_single_prediction(self):
        """Test 4: Make a single prediction"""
        prediction, error = self.predictor.predict_next_hour()
        
        if error:
            print(f"  ❌ {error}")
            return
        
        print(f"  • Current load: {prediction['current_load_kw']} kW")
        print(f"  • Predicted load: {prediction['predicted_load_kw']} kW")
        print(f"  • Confidence interval: [{prediction['confidence_interval']['lower']}, {prediction['confidence_interval']['upper']}] kW")
        print(f"  • Prediction for: {prediction['prediction_for']}")
        
        print("\n  Features used:")
        for key, value in prediction['features_used'].items():
            print(f"    • {key}: {value}")
    
    def _test_rolling_predictions(self, hours=24):
        """Test 5: Test predictions on historical data (rolling window)"""
        
        # Get historical data
        latest_time = db.session.query(db.func.max(EnergyLog.timestamp)).scalar()
        test_start = latest_time - timedelta(hours=hours)
        
        # Get actual values
        actual_loads = db.session.query(
            EnergyLog.timestamp,
            db.func.sum(EnergyLog.total_load).label('campus_load')
        ).filter(
            EnergyLog.timestamp >= test_start,
            EnergyLog.timestamp <= latest_time
        ).group_by(EnergyLog.timestamp).order_by(EnergyLog.timestamp).all()
        
        if len(actual_loads) < 2:
            print("  ⚠️  Not enough historical data for rolling predictions")
            return
        
        predictions = []
        actuals = []
        timestamps = []
        
        # Make predictions for each hour
        for i in range(1, len(actual_loads)):
            actual_load = actual_loads[i].campus_load
            timestamp = actual_loads[i].timestamp
            
            # Use previous hour's data for prediction
            prev_load = actual_loads[i-1].campus_load
            
            # Get features for this timestamp
            logs_at_time = EnergyLog.query.filter(
                EnergyLog.timestamp == actual_loads[i-1].timestamp
            ).all()
            
            if not logs_at_time:
                continue
            
            avg_temp = np.mean([log.temperature for log in logs_at_time])
            occupancy_rate = sum(log.occupancy for log in logs_at_time) / len(logs_at_time)
            
            # Create feature vector
            features = pd.DataFrame([{
                'hour': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
                'avg_temperature': avg_temp,
                'occupancy_rate': occupancy_rate,
                'last_hour_load': prev_load
            }])
            
            # Predict
            predicted_load = self.predictor.model.predict(features)[0]
            
            predictions.append(predicted_load)
            actuals.append(actual_load)
            timestamps.append(timestamp)
        
        # Calculate metrics
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        r2 = r2_score(actuals, predictions)
        mape = np.mean(np.abs((np.array(actuals) - np.array(predictions)) / np.array(actuals))) * 100
        
        print(f"  • Predictions made: {len(predictions)}")
        print(f"  • Mean Absolute Error: {mae:.2f} kW")
        print(f"  • Root Mean Square Error: {rmse:.2f} kW")
        print(f"  • R² Score: {r2:.4f}")
        print(f"  • Mean Absolute Percentage Error: {mape:.2f}%")
        
        self.test_results.append({
            'test': 'Rolling Predictions',
            'predictions': len(predictions),
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'r2': round(r2, 4),
            'mape': round(mape, 2)
        })
        
        # Show sample predictions
        print("\n  Sample predictions (last 5 hours):")
        for i in range(max(0, len(predictions)-5), len(predictions)):
            error_pct = abs(actuals[i] - predictions[i]) / actuals[i] * 100
            print(f"    {timestamps[i].strftime('%Y-%m-%d %H:%M')} | Actual: {actuals[i]:.2f} kW | Predicted: {predictions[i]:.2f} kW | Error: {error_pct:.1f}%")
    
    def _test_peak_vs_offpeak(self):
        """Test 6: Compare prediction accuracy during peak and off-peak hours"""
        
        # Peak hours: 9 AM - 5 PM
        # Off-peak: 6 PM - 8 AM
        
        latest_time = db.session.query(db.func.max(EnergyLog.timestamp)).scalar()
        test_start = latest_time - timedelta(days=3)
        
        actual_loads = db.session.query(
            EnergyLog.timestamp,
            db.func.sum(EnergyLog.total_load).label('campus_load')
        ).filter(
            EnergyLog.timestamp >= test_start
        ).group_by(EnergyLog.timestamp).order_by(EnergyLog.timestamp).all()
        
        peak_predictions = []
        peak_actuals = []
        offpeak_predictions = []
        offpeak_actuals = []
        
        for i in range(1, len(actual_loads)):
            actual_load = actual_loads[i].campus_load
            timestamp = actual_loads[i].timestamp
            prev_load = actual_loads[i-1].campus_load
            
            logs_at_time = EnergyLog.query.filter(
                EnergyLog.timestamp == actual_loads[i-1].timestamp
            ).all()
            
            if not logs_at_time:
                continue
            
            avg_temp = np.mean([log.temperature for log in logs_at_time])
            occupancy_rate = sum(log.occupancy for log in logs_at_time) / len(logs_at_time)
            
            features = pd.DataFrame([{
                'hour': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
                'avg_temperature': avg_temp,
                'occupancy_rate': occupancy_rate,
                'last_hour_load': prev_load
            }])
            
            predicted_load = self.predictor.model.predict(features)[0]
            
            # Classify as peak or off-peak
            if 9 <= timestamp.hour <= 17:
                peak_predictions.append(predicted_load)
                peak_actuals.append(actual_load)
            else:
                offpeak_predictions.append(predicted_load)
                offpeak_actuals.append(actual_load)
        
        if peak_predictions:
            peak_mae = mean_absolute_error(peak_actuals, peak_predictions)
            peak_mape = np.mean(np.abs((np.array(peak_actuals) - np.array(peak_predictions)) / np.array(peak_actuals))) * 100
            print(f"  Peak Hours (9 AM - 5 PM):")
            print(f"    • Predictions: {len(peak_predictions)}")
            print(f"    • MAE: {peak_mae:.2f} kW")
            print(f"    • MAPE: {peak_mape:.2f}%")
        
        if offpeak_predictions:
            offpeak_mae = mean_absolute_error(offpeak_actuals, offpeak_predictions)
            offpeak_mape = np.mean(np.abs((np.array(offpeak_actuals) - np.array(offpeak_predictions)) / np.array(offpeak_actuals))) * 100
            print(f"\n  Off-Peak Hours (6 PM - 8 AM):")
            print(f"    • Predictions: {len(offpeak_predictions)}")
            print(f"    • MAE: {offpeak_mae:.2f} kW")
            print(f"    • MAPE: {offpeak_mape:.2f}%")
    
    def _test_weekday_vs_weekend(self):
        """Test 7: Compare weekday vs weekend prediction accuracy"""
        
        latest_time = db.session.query(db.func.max(EnergyLog.timestamp)).scalar()
        test_start = latest_time - timedelta(days=7)
        
        actual_loads = db.session.query(
            EnergyLog.timestamp,
            db.func.sum(EnergyLog.total_load).label('campus_load')
        ).filter(
            EnergyLog.timestamp >= test_start
        ).group_by(EnergyLog.timestamp).order_by(EnergyLog.timestamp).all()
        
        weekday_predictions = []
        weekday_actuals = []
        weekend_predictions = []
        weekend_actuals = []
        
        for i in range(1, len(actual_loads)):
            actual_load = actual_loads[i].campus_load
            timestamp = actual_loads[i].timestamp
            prev_load = actual_loads[i-1].campus_load
            
            logs_at_time = EnergyLog.query.filter(
                EnergyLog.timestamp == actual_loads[i-1].timestamp
            ).all()
            
            if not logs_at_time:
                continue
            
            avg_temp = np.mean([log.temperature for log in logs_at_time])
            occupancy_rate = sum(log.occupancy for log in logs_at_time) / len(logs_at_time)
            
            features = pd.DataFrame([{
                'hour': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
                'avg_temperature': avg_temp,
                'occupancy_rate': occupancy_rate,
                'last_hour_load': prev_load
            }])
            
            predicted_load = self.predictor.model.predict(features)[0]
            
            # Classify as weekday or weekend
            if timestamp.weekday() < 5:
                weekday_predictions.append(predicted_load)
                weekday_actuals.append(actual_load)
            else:
                weekend_predictions.append(predicted_load)
                weekend_actuals.append(actual_load)
        
        if weekday_predictions:
            weekday_mae = mean_absolute_error(weekday_actuals, weekday_predictions)
            weekday_mape = np.mean(np.abs((np.array(weekday_actuals) - np.array(weekday_predictions)) / np.array(weekday_actuals))) * 100
            print(f"  Weekdays (Mon-Fri):")
            print(f"    • Predictions: {len(weekday_predictions)}")
            print(f"    • MAE: {weekday_mae:.2f} kW")
            print(f"    • MAPE: {weekday_mape:.2f}%")
        
        if weekend_predictions:
            weekend_mae = mean_absolute_error(weekend_actuals, weekend_predictions)
            weekend_mape = np.mean(np.abs((np.array(weekend_actuals) - np.array(weekend_predictions)) / np.array(weekend_actuals))) * 100
            print(f"\n  Weekends (Sat-Sun):")
            print(f"    • Predictions: {len(weekend_predictions)}")
            print(f"    • MAE: {weekend_mae:.2f} kW")
            print(f"    • MAPE: {weekend_mape:.2f}%")
    
    def _generate_test_report(self):
        """Generate JSON test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results
        }
        
        with open('prediction_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: prediction_test_report.json")

def run_prediction_tests():
    """Main function to run all tests"""
    from app import create_app
    app = create_app()
    
    with app.app_context():
        tester = PredictionTester()
        tester.run_comprehensive_tests()

if __name__ == "__main__":
    run_prediction_tests()