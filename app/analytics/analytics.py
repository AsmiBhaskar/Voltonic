from app.models import db, EnergyLog, Room, Building, Faculty
from sqlalchemy import func
from datetime import datetime, timedelta

class EnergyAnalytics:
    """Analytics engine for energy consumption data"""
    
    @staticmethod
    def get_live_campus_load():
        """Get current total campus energy consumption"""
        latest_timestamp = db.session.query(func.max(EnergyLog.timestamp)).scalar()
        
        if not latest_timestamp:
            return {'error': 'No data available'}
        
        total_load = db.session.query(
            func.sum(EnergyLog.total_load)
        ).filter(
            EnergyLog.timestamp == latest_timestamp
        ).scalar() or 0.0
        
        optimized_count = db.session.query(
            func.count(EnergyLog.id)
        ).filter(
            EnergyLog.timestamp == latest_timestamp,
            EnergyLog.optimized == True
        ).scalar() or 0
        
        total_rooms = Room.query.count()
        
        return {
            'timestamp': latest_timestamp.isoformat(),
            'total_load_kw': round(total_load, 2),
            'total_rooms': total_rooms,
            'optimized_rooms': optimized_count,
            'optimization_percentage': round((optimized_count / total_rooms) * 100, 2) if total_rooms > 0 else 0
        }
    
    @staticmethod
    def get_building_load(building_id):
        """Get current load for a specific building"""
        latest_timestamp = db.session.query(func.max(EnergyLog.timestamp)).scalar()
        
        if not latest_timestamp:
            return {'error': 'No data available'}
        
        # Get all rooms in this building
        rooms = db.session.query(Room.id).join(
            Room.floor
        ).filter(
            Room.floor.has(building_id=building_id)
        ).all()
        
        room_ids = [r.id for r in rooms]
        
        total_load = db.session.query(
            func.sum(EnergyLog.total_load)
        ).filter(
            EnergyLog.timestamp == latest_timestamp,
            EnergyLog.room_id.in_(room_ids)
        ).scalar() or 0.0
        
        building = Building.query.get(building_id)
        
        return {
            'building_id': building_id,
            'building_name': building.name if building else 'Unknown',
            'timestamp': latest_timestamp.isoformat(),
            'total_load_kw': round(total_load, 2),
            'total_rooms': len(room_ids)
        }
    
    @staticmethod
    def get_hourly_consumption(hours=24):
        """Get hourly average consumption for last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        hourly_data = db.session.query(
            func.strftime('%Y-%m-%d %H:00:00', EnergyLog.timestamp).label('hour'),
            func.avg(EnergyLog.total_load).label('avg_load'),
            func.sum(EnergyLog.total_load).label('total_load'),
            func.count(EnergyLog.id).label('reading_count')
        ).filter(
            EnergyLog.timestamp >= cutoff_time
        ).group_by('hour').order_by('hour').all()
        
        return [
            {
                'hour': row.hour,
                'avg_load_kw': round(row.avg_load, 2),
                'total_load_kw': round(row.total_load, 2),
                'readings': row.reading_count
            }
            for row in hourly_data
        ]
    
    @staticmethod
    def get_building_comparison():
        """Compare energy usage across all buildings"""
        latest_timestamp = db.session.query(func.max(EnergyLog.timestamp)).scalar()
        
        if not latest_timestamp:
            return {'error': 'No data available'}
        
        buildings = Building.query.all()
        comparison = []
        
        for building in buildings:
            load_data = EnergyAnalytics.get_building_load(building.id)
            comparison.append(load_data)
        
        # Sort by load descending
        comparison.sort(key=lambda x: x.get('total_load_kw', 0), reverse=True)
        
        return comparison
    
    @staticmethod
    def get_daily_summary(days=7):
        """Get daily consumption summary for last N days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        daily_data = db.session.query(
            func.date(EnergyLog.timestamp).label('date'),
            func.sum(EnergyLog.total_load).label('total_load'),
            func.count(EnergyLog.id).label('reading_count'),
            func.count(func.nullif(EnergyLog.optimized, False)).label('optimized_count')
        ).filter(
            EnergyLog.timestamp >= cutoff_time
        ).group_by('date').order_by('date').all()
        
        return [
            {
                'date': row.date,
                'total_load_kw': round(row.total_load, 2),
                'readings': row.reading_count,
                'optimized': row.optimized_count,
                'optimization_rate': round((row.optimized_count / row.reading_count) * 100, 2) if row.reading_count > 0 else 0
            }
            for row in daily_data
        ]