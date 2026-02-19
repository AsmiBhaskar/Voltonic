import random
import time
import json
from datetime import datetime
from sqlalchemy.exc import OperationalError
from app.models import (
    db, Room, Timetable, EnergyLog, EnergySource, GridStatus, Building,
    AutonomousLog, CancellationPattern, PowerSourceConfig
)
from app.optimization.optimizer import EnergyOptimizer
from app.optimization.smart_power_controller import SmartPowerController


class IoTSimulator:
    """Simulates IoT sensor data for all rooms every 60 seconds
    
    Enhanced with:
    - Configurable cancellation probability per room type
    - Solar capacity limits (452 kW per building)
    - Reduced solar after 6 PM
    - Demand spike detection
    - ML-driven auto-cutoff for frequently cancelled classes
    """
    
    # Cancellation probabilities by room type (configurable)
    CANCELLATION_PROBABILITY = {
        'classroom': 0.25,    # 25% chance class is cancelled even if scheduled
        'Smart_Class': 0.15,  # 15% for smart classes
        'lab': 0.10,          # 10% for labs (more important)
        'staff': 0.05         # 5% for staff rooms
    }
    
    # Solar configuration
    SOLAR_CAPACITY_PER_BUILDING = 452.0  # kW
    
    # Track previous building loads for spike detection
    _previous_building_loads = {}
    
    @staticmethod
    def get_grid_status():
        """Get current grid availability status"""
        latest_status = GridStatus.query.order_by(GridStatus.timestamp.desc()).first()
        if latest_status:
            return latest_status.grid_available
        return True  # Default to grid available
    
    @staticmethod
    def get_solar_availability():
        """Get solar availability factor based on time of day"""
        current_hour = datetime.now().hour
        return SmartPowerController.get_solar_availability(current_hour)
    
    @staticmethod
    def select_energy_source_smart(room, building_id, room_load, grid_available):
        """Smart energy source selection with hybrid mode support
        
        Logic:
        - Check solar capacity limits
        - Activate hybrid mode if needed
        - Use grid when solar unavailable
        """
        sources = {src.name: src for src in EnergySource.query.all()}
        
        if not sources:
            return None, None
        
        current_hour = datetime.now().hour
        solar_availability = SmartPowerController.get_solar_availability(current_hour)
        
        # Get or create power config for building
        config = PowerSourceConfig.query.filter_by(building_id=building_id).first()
        if not config:
            config = PowerSourceConfig(
                building_id=building_id,
                solar_capacity_kw=IoTSimulator.SOLAR_CAPACITY_PER_BUILDING
            )
            db.session.add(config)
        
        effective_solar_capacity = config.solar_capacity_kw * solar_availability
        
        # If solar unavailable (night), use grid
        if solar_availability == 0:
            grid_source = sources.get('grid')
            return grid_source.id if grid_source else None, 'grid_only'
        
        # If grid not available, use solar (limited) or diesel
        if not grid_available:
            if room.type in ['classroom', 'staff']:
                solar_source = sources.get('solar')
                return solar_source.id if solar_source else None, 'solar_only'
            else:
                diesel_source = sources.get('diesel')
                return diesel_source.id if diesel_source else None, 'diesel'
        
        # Normal operation: prioritize solar if capacity available
        # Get current building load
        current_building_load = IoTSimulator._get_building_current_load(building_id)
        
        if current_building_load + room_load <= effective_solar_capacity:
            # Solar can handle it
            solar_source = sources.get('solar')
            return solar_source.id if solar_source else None, 'solar_only'
        else:
            # Need hybrid mode
            config.hybrid_mode_active = True
            grid_source = sources.get('grid')
            return grid_source.id if grid_source else None, 'hybrid'
    
    @staticmethod
    def _get_building_current_load(building_id):
        """Get current total load for a building"""
        latest_time = db.session.query(db.func.max(EnergyLog.timestamp)).scalar()
        if not latest_time:
            return 0.0
        
        # Get rooms in this building
        building = Building.query.get(building_id)
        if not building:
            return 0.0
        
        room_ids = []
        for floor in building.floors:
            room_ids.extend([room.id for room in floor.rooms])
        
        if not room_ids:
            return 0.0
        
        total_load = db.session.query(db.func.sum(EnergyLog.total_load)).filter(
            EnergyLog.room_id.in_(room_ids),
            EnergyLog.timestamp == latest_time
        ).scalar() or 0.0
        
        return total_load
    
    @staticmethod
    def is_room_scheduled(room_id, current_time):
        """Check if room has a scheduled class at current time"""
        day_of_week = current_time.weekday()
        current_time_only = current_time.time()
        
        schedules = Timetable.query.filter_by(
            room_id=room_id,
            day_of_week=day_of_week
        ).all()
        
        for schedule in schedules:
            if schedule.start_time <= current_time_only <= schedule.end_time:
                return True
        return False
    
    @staticmethod
    def simulate_cancellation(room_type, room_id, day_of_week, hour):
        """
        Determine if a scheduled class is actually cancelled
        Uses ML patterns if available, otherwise uses base probability
        """
        # First check ML-based pattern
        should_cutoff, cancellation_rate = SmartPowerController.should_auto_cutoff(
            room_id, day_of_week, hour
        )
        
        if should_cutoff:
            # ML says this class is usually cancelled
            return True, 'ml_prediction', cancellation_rate
        
        # Otherwise use base probability for room type
        base_prob = IoTSimulator.CANCELLATION_PROBABILITY.get(room_type, 0.1)
        is_cancelled = random.random() < base_prob
        
        return is_cancelled, 'random', base_prob
    
    @staticmethod
    def calculate_loads(room, is_scheduled, temperature, is_cancelled=False):
        """Calculate all energy loads for a room with cancellation support"""
        
        # Determine occupancy
        if is_scheduled and not is_cancelled:
            occupancy = True
        elif is_cancelled:
            occupancy = False  # Class was cancelled
        else:
            # 10% chance of random occupancy (maintenance, etc.)
            occupancy = random.random() < 0.1
        
        base_load = room.base_load_kw
        
        # Equipment Load
        if room.type == "classroom":
            equipment_load = round(random.uniform(0.2, 0.5), 2) if occupancy else 0.1
        elif room.type == "Smart_Class":
            equipment_load = round(random.uniform(3.0, 4.5), 2) if occupancy else 0.5
        elif room.type == "lab":
            equipment_load = round(random.uniform(2.5, 4.0), 2) if occupancy else 0.3
        else:  # staff room
            equipment_load = round(random.uniform(0.3, 0.7), 2)
        
        # AC Load (temperature-dependent)
        if temperature > 29 and occupancy:
            ac_load = round(random.uniform(1.5, 2.0), 2)
        else:
            ac_load = 0.2
        
        # Light Load
        if occupancy:
            light_load = round(random.uniform(0.3, 0.5), 2)
        else:
            light_load = 0.05
        
        total_load = round(base_load + ac_load + light_load + equipment_load, 2)
        
        return {
            'occupancy': occupancy,
            'temperature': temperature,
            'base_load': base_load,
            'ac_load': ac_load,
            'light_load': light_load,
            'equipment_load': equipment_load,
            'total_load': total_load,
            'optimized': False
        }
    
    @staticmethod
    def check_and_handle_demand_spike(building_id, current_load):
        """Check for demand spikes and switch to hybrid if needed"""
        previous_load = IoTSimulator._previous_building_loads.get(building_id, 0)
        
        is_spike, load_increase = SmartPowerController.check_demand_spike(
            building_id, current_load, previous_load
        )
        
        if is_spike:
            # Trigger hybrid mode
            result, error = SmartPowerController.switch_to_hybrid_mode(
                building_id,
                current_load,
                IoTSimulator.SOLAR_CAPACITY_PER_BUILDING * SmartPowerController.get_solar_availability(datetime.now().hour),
                f"Demand spike detected: +{load_increase:.2f} kW (threshold: {SmartPowerController.DEMAND_SPIKE_THRESHOLD} kW)"
            )
            
            if result:
                print(f"⚡ DEMAND SPIKE: Building {building_id} switched to hybrid mode (+{load_increase:.2f} kW)")
        
        # Update previous load
        IoTSimulator._previous_building_loads[building_id] = current_load
        
        return is_spike
    
    @staticmethod
    def simulate_all_rooms():
        """Run simulation for all rooms with ML-driven optimization"""
        current_time = datetime.now()
        day_of_week = current_time.weekday()
        hour = current_time.hour
        rooms = Room.query.all()
        
        # Get current grid status
        grid_available = IoTSimulator.get_grid_status()
        solar_availability = IoTSimulator.get_solar_availability()
        
        logs_created = 0
        optimizations_applied = 0
        auto_cutoffs = 0
        batch_size = 100
        
        # Track building loads for spike detection
        building_loads = {}
        
        for idx, room in enumerate(rooms):
            # Get building ID through floor relationship
            building_id = room.floor.building_id
            
            # Generate random temperature (24-36°C)
            temperature = round(random.uniform(24, 36), 1)
            
            # Check schedule
            is_scheduled = IoTSimulator.is_room_scheduled(room.id, current_time)
            
            # Simulate potential cancellation
            is_cancelled = False
            cancellation_reason = None
            if is_scheduled:
                is_cancelled, method, rate = IoTSimulator.simulate_cancellation(
                    room.type, room.id, day_of_week, hour
                )
                if is_cancelled:
                    cancellation_reason = f"{method}: {rate*100:.1f}% cancellation rate"
            
            # Calculate loads
            load_data = IoTSimulator.calculate_loads(room, is_scheduled, temperature, is_cancelled)
            
            # Select appropriate energy source (smart selection)
            energy_source_id, power_mode = IoTSimulator.select_energy_source_smart(
                room, building_id, load_data['total_load'], grid_available
            )
            
            if energy_source_id is None:
                continue
            
            # Create energy log
            energy_log = EnergyLog(
                room_id=room.id,
                energy_source_id=energy_source_id,
                timestamp=current_time,
                **load_data
            )
            
            # Check for ML-driven auto-cutoff
            should_cutoff, cutoff_rate = SmartPowerController.should_auto_cutoff(
                room.id, day_of_week, hour
            )
            
            if should_cutoff and is_scheduled:
                # Apply alpha-beta cutoff
                energy_saved = SmartPowerController.apply_alpha_beta_cutoff(
                    room, energy_log,
                    f"ML-predicted cancellation (historical rate: {cutoff_rate*100:.1f}%)"
                )
                auto_cutoffs += 1
            else:
                # Apply standard optimization
                EnergyOptimizer.optimize_room_log(energy_log, room, is_scheduled and not is_cancelled)
            
            if energy_log.optimized:
                optimizations_applied += 1
            
            # Update cancellation pattern for ML learning
            if is_scheduled:
                SmartPowerController.update_cancellation_pattern(
                    room.id, day_of_week, hour, load_data['occupancy']
                )
            
            # Track building load for spike detection
            if building_id not in building_loads:
                building_loads[building_id] = 0
            building_loads[building_id] += energy_log.total_load
            
            db.session.add(energy_log)
            logs_created += 1
            
            # Commit in batches
            if (idx + 1) % batch_size == 0:
                IoTSimulator._commit_with_retry()
        
        # Check for demand spikes per building
        spikes_detected = 0
        for building_id, current_load in building_loads.items():
            if IoTSimulator.check_and_handle_demand_spike(building_id, current_load):
                spikes_detected += 1
        
        # Final commit
        IoTSimulator._commit_with_retry()
        
        # Enhanced logging
        status_parts = [
            f"📊 Simulated {logs_created} rooms",
            f"✅ Optimized {optimizations_applied}",
        ]
        if auto_cutoffs > 0:
            status_parts.append(f"🔌 Auto-cutoff {auto_cutoffs}")
        if spikes_detected > 0:
            status_parts.append(f"⚡ Spikes {spikes_detected}")
        if solar_availability < 1.0:
            status_parts.append(f"☀️ Solar {int(solar_availability*100)}%")
        
        print(f" {' | '.join(status_parts)} at {current_time.strftime('%H:%M:%S')}")
        
        return logs_created, optimizations_applied
    
    @staticmethod
    def _commit_with_retry(max_retries=3, initial_wait=0.1):
        """Commit database session with retry logic for lock errors"""
        for attempt in range(max_retries):
            try:
                db.session.commit()
                return True
            except OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    wait_time = initial_wait * (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)
                    db.session.rollback()
                else:
                    db.session.rollback()
                    raise
        return False