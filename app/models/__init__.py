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
    type = db.Column(db.String(20), nullable=False)  # classroom/lab/staff
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

class EnergyLog(db.Model):
    __tablename__ = 'energy_log'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    occupancy = db.Column(db.Boolean, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    base_load = db.Column(db.Float, nullable=False)
    ac_load = db.Column(db.Float, nullable=False)
    light_load = db.Column(db.Float, nullable=False)
    equipment_load = db.Column(db.Float, nullable=False)
    total_load = db.Column(db.Float, nullable=False)
    optimized = db.Column(db.Boolean, default=False)