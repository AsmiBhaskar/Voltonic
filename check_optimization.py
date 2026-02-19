from app import create_app
from app.models import db, EnergyLog, EnergySource, Room

app = create_app()

with app.app_context():
    # Get energy sources
    solar = EnergySource.query.filter_by(name='solar').first()
    grid = EnergySource.query.filter_by(name='grid').first()
    
    # Check current hour
    from datetime import datetime
    current_hour = datetime.now().hour
    print(f"\n⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📊 Current Hour: {current_hour}")
    print(f"🔆 Peak Solar Hours: 10 AM - 3 PM (10-14)")
    
    if 10 <= current_hour < 15:
        print("✅ Currently in PEAK SOLAR hours - optimization should be active\n")
    else:
        print("❌ Currently OUTSIDE peak solar hours - no solar switching expected\n")
    
    # Get stats
    total_logs = EnergyLog.query.count()
    total_optimized = EnergyLog.query.filter_by(optimized=True).count()
    solar_logs = EnergyLog.query.filter_by(energy_source_id=solar.id).count()
    grid_logs = EnergyLog.query.filter_by(energy_source_id=grid.id).count()
    
    print(f"📈 Database Statistics:")
    print(f"   Total Energy Logs: {total_logs:,}")
    print(f"   Optimized Logs: {total_optimized:,}")
    print(f"   Solar Energy Logs: {solar_logs:,}")
    print(f"   Grid Energy Logs: {grid_logs:,}")
    
    # Check classrooms using solar
    latest_logs = EnergyLog.query.order_by(EnergyLog.timestamp.desc()).limit(5).all()
    print(f"\n🔍 Latest 5 Energy Logs:")
    for log in latest_logs:
        room = Room.query.get(log.room_id)
        source = EnergySource.query.get(log.energy_source_id)
        opt_status = "✅ OPTIMIZED" if log.optimized else "⚪ Regular"
        print(f"   {log.timestamp.strftime('%H:%M:%S')} | Room {log.room_id} ({room.type}) | {source.name} | {opt_status}")
    
    # Count classrooms on solar (during peak hours if applicable)
    if 10 <= current_hour < 15:
        classroom_solar = db.session.query(EnergyLog).join(Room).filter(
            Room.type.in_(['classroom', 'Smart_Class']),
            EnergyLog.energy_source_id == solar.id,
            EnergyLog.optimized == True
        ).count()
        
        print(f"\n🌞 Classrooms/Smart Classes switched to SOLAR (optimized): {classroom_solar:,}")
