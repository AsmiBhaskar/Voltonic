from app import create_app
from app.models import db, Room, EnergyLog
from app.utils.seed_data import seed_campus
from app.simulation.engine import IoTSimulator
# from app.prediction.predictor import EnergyPredictor  # Temporarily disabled for fast startup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import atexit

# Create Flask app
app = create_app()

# Global predictor instance
# predictor = EnergyPredictor()  # Temporarily disabled
predictor = None

def initialize_database():
    """Check if database needs seeding"""
    with app.app_context():
        room_count = Room.query.count()
        
        if room_count == 0:
            print("\n📦 Database is empty. Starting seed process...\n")
            seed_campus()
            print("\n✅ Database seeded successfully!\n")
        else:
            print(f"\n✅ Database already contains {room_count} rooms\n")

def run_simulation_job():
    """Scheduled job to simulate IoT data every 60 seconds"""
    with app.app_context():
        try:
            IoTSimulator.simulate_all_rooms()
        except Exception as e:
            print(f"❌ Simulation error: {e}")

def train_ml_model_job():
    """Scheduled job to retrain ML model daily"""
    if predictor is None:
        return  # Skip if predictor not initialized
    
    with app.app_context():
        try:
            print("\n🤖 Starting scheduled model retraining...")
            predictor.train_model(hours_back=168)
        except Exception as e:
            print(f"❌ Model training error: {e}")

def check_and_train_initial_model():
    """Train model if enough data exists"""
    if predictor is None:
        print("\n⏭️  ML predictor disabled for fast startup\n")
        return  # Skip if predictor not initialized
    
    with app.app_context():
        # Check if we have enough data (at least 2 hours of logs)
        cutoff = datetime.now() - timedelta(hours=2)
        log_count = EnergyLog.query.filter(EnergyLog.timestamp >= cutoff).count()
        
        if log_count >= 100:
            print("\n🤖 Sufficient data found. Training initial ML model...")
            success, result = predictor.train_model(hours_back=24)
            if success:
                print(f"✅ Initial model trained! MAE: {result['mae']} kW\n")
        else:
            print(f"\n⏳ Not enough data yet ({log_count}/100 records). Model will train once sufficient data is available.\n")

def start_simulation_scheduler():
    """Start background scheduler for IoT simulation"""
    scheduler = BackgroundScheduler()
    
    # Run simulation every 60 seconds
    scheduler.add_job(
        func=run_simulation_job,
        trigger="interval",
        seconds=60,
        id="iot_simulation",
        name="IoT Data Simulation",
        replace_existing=True
    )
    
    # Retrain ML model every 24 hours (only if predictor is initialized)
    if predictor is not None:
        scheduler.add_job(
            func=train_ml_model_job,
            trigger="interval",
            hours=24,
            id="ml_training",
            name="ML Model Retraining",
            replace_existing=True
        )
    
    scheduler.start()
    print("🔄 IoT Simulation Scheduler started (60-second interval)")
    if predictor is not None:
        print("🤖 ML Model Retraining scheduled (24-hour interval)")
    else:
        print("⏭️  ML Model training disabled (uncomment predictor imports to enable)")
    
    # Run first simulation immediately
    run_simulation_job()
    
    # Check if we can train initial model
    check_and_train_initial_model()
    
    # Shutdown scheduler on exit
    atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    print("⚡ VOLTONIC Backend Starting...\n")
    
    # Initialize database
    initialize_database()
    
    # Start IoT simulation
    start_simulation_scheduler()
    
    # Run Flask app
    print("\n🚀 Starting Flask server on http://127.0.0.1:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)