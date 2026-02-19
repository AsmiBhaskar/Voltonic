from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    buildings = db.relationship('Building', backref='faculty', lazy=True)

class Building(db.Model):
    __tablename__ = 'building'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    floors = db.relationship('Floor', backref='building', lazy=True)

class Floor(db.Model):
    __tablename__ = 'floor'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    rooms = db.relationship('Room', backref='floor', lazy=True)

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # classroom/lab/staff/Smart_Class
    capacity = db.Column(db.Integer, nullable=False)
    base_load_kw = db.Column(db.Float, nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'), nullable=False)
    timetables = db.relationship('Timetable', backref='room', lazy=True)
    energy_logs = db.relationship('EnergyLog', backref='room', lazy=True)

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (Monday-Sunday)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class EnergySource(db.Model):
    __tablename__ = 'energy_source'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # grid/solar/diesel
    cost_per_kwh = db.Column(db.Float, nullable=False)  # Cost in $/kWh
    is_available = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, nullable=False)  # 1=highest priority
    energy_logs = db.relationship('EnergyLog', backref='energy_source', lazy=True)

class GridStatus(db.Model):
    __tablename__ = 'grid_status'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    grid_available = db.Column(db.Boolean, nullable=False, default=True)
    reason = db.Column(db.String(200))  # Reason for outage if any

class EnergyLog(db.Model):
    __tablename__ = 'energy_log'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    energy_source_id = db.Column(db.Integer, db.ForeignKey('energy_source.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    occupancy = db.Column(db.Boolean, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    base_load = db.Column(db.Float, nullable=False)
    ac_load = db.Column(db.Float, nullable=False)
    light_load = db.Column(db.Float, nullable=False)
    equipment_load = db.Column(db.Float, nullable=False)
    total_load = db.Column(db.Float, nullable=False)
    optimized = db.Column(db.Boolean, default=False)


class AutonomousLog(db.Model):
    """Logs all autonomous system actions for audit and analytics"""
    __tablename__ = 'autonomous_log'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    # Action types: 
    # - POWER_CUTOFF: Auto power cut due to predicted cancellation
    # - SOURCE_SWITCH: Switched energy source (solar->grid, etc.)
    # - HYBRID_MODE: Activated hybrid power mode
    # - DEMAND_SPIKE: Detected demand spike
    # - PREDICTIVE_SWITCH: Proactive source switch based on ML prediction
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True, index=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=True)
    reason = db.Column(db.String(500), nullable=False)
    energy_saved_kwh = db.Column(db.Float, default=0.0)
    previous_state = db.Column(db.String(200))  # JSON string of previous state
    new_state = db.Column(db.String(200))  # JSON string of new state
    is_optimization = db.Column(db.Boolean, default=True)
    confidence_score = db.Column(db.Float)  # ML prediction confidence (0-1)
    
    room = db.relationship('Room', backref='autonomous_logs')
    building = db.relationship('Building', backref='autonomous_logs')


class CancellationPattern(db.Model):
    """Tracks class cancellation patterns for ML predictions"""
    __tablename__ = 'cancellation_pattern'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6
    hour = db.Column(db.Integer, nullable=False)  # 0-23
    scheduled_count = db.Column(db.Integer, default=0)  # Times scheduled
    occupied_count = db.Column(db.Integer, default=0)  # Times actually occupied
    cancellation_rate = db.Column(db.Float, default=0.0)  # occupied/scheduled
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    auto_cutoff_enabled = db.Column(db.Boolean, default=False)  # If >50% cancellation
    
    room = db.relationship('Room', backref='cancellation_patterns')
    
    __table_args__ = (
        db.UniqueConstraint('room_id', 'day_of_week', 'hour', name='unique_room_day_hour'),
    )


class PowerSourceConfig(db.Model):
    """Configuration for smart power source management"""
    __tablename__ = 'power_source_config'
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False, unique=True)
    solar_capacity_kw = db.Column(db.Float, default=452.0)  # Max solar capacity
    current_solar_output_kw = db.Column(db.Float, default=0.0)
    grid_capacity_kw = db.Column(db.Float, default=1000.0)  # Max grid capacity
    demand_spike_threshold_kw = db.Column(db.Float, default=2.0)  # Threshold for spike
    hybrid_mode_active = db.Column(db.Boolean, default=False)
    last_source_switch = db.Column(db.DateTime)
    
    building = db.relationship('Building', backref='power_config')