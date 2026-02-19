"""
Smart Power Controller - Autonomous power management system
Handles:
- Class cancellation pattern detection and auto-cutoff
- Solar to grid switching on demand spikes
- Hybrid power mode management
- Predictive source switching (30 min ahead)
- Gradual power transitions
"""

import json
from datetime import datetime, timedelta
from app.models import (
    db, Room, EnergyLog, EnergySource, Timetable, Building,
    AutonomousLog, CancellationPattern, PowerSourceConfig
)


class SmartPowerController:
    """Intelligent power management system with ML-driven decisions"""
    
    # Configuration constants
    CANCELLATION_THRESHOLD = 0.50  # 50% cancellation rate triggers auto-cutoff
    OBSERVATION_DAYS = 7  # 1 week of observation required
    DEMAND_SPIKE_THRESHOLD = 2.0  # kW increase triggers source switch
    SOLAR_CAPACITY_PER_BUILDING = 452.0  # kW
    SOLAR_EVENING_REDUCTION = 0.3  # 30% capacity after 6 PM
    TRANSITION_STEPS = 6  # Gradual transition over 30 min (5 min per step)
    
    @staticmethod
    def get_solar_availability(current_hour):
        """
        Get solar availability factor based on time of day
        - Full availability: 6 AM - 6 PM (6-18)
        - Reduced after 6 PM (30% capacity)
        - None at night (0% after 8 PM)
        """
        if 6 <= current_hour < 18:
            return 1.0  # Full solar
        elif 18 <= current_hour < 20:
            return 0.3  # Reduced solar (evening)
        else:
            return 0.0  # No solar (night)
    
    @staticmethod
    def analyze_cancellation_patterns(room_id, day_of_week=None, hour=None):
        """
        Analyze historical data to detect class cancellation patterns
        Returns cancellation rate and whether auto-cutoff should be enabled
        """
        # Get data from last 7 days
        cutoff_date = datetime.now() - timedelta(days=SmartPowerController.OBSERVATION_DAYS)
        
        query = db.session.query(
            EnergyLog.timestamp,
            EnergyLog.occupancy
        ).join(Timetable, Timetable.room_id == EnergyLog.room_id).filter(
            EnergyLog.room_id == room_id,
            EnergyLog.timestamp >= cutoff_date
        )
        
        if day_of_week is not None:
            query = query.filter(Timetable.day_of_week == day_of_week)
        
        logs = query.all()
        
        if len(logs) < 10:  # Not enough data
            return {
                'cancellation_rate': 0.0,
                'auto_cutoff_recommended': False,
                'sample_count': len(logs),
                'message': 'Insufficient data for analysis'
            }
        
        # Count scheduled vs occupied
        scheduled_count = len(logs)
        occupied_count = sum(1 for log in logs if log.occupancy)
        
        cancellation_rate = 1 - (occupied_count / scheduled_count) if scheduled_count > 0 else 0
        
        return {
            'cancellation_rate': round(cancellation_rate, 3),
            'auto_cutoff_recommended': cancellation_rate >= SmartPowerController.CANCELLATION_THRESHOLD,
            'scheduled_count': scheduled_count,
            'occupied_count': occupied_count,
            'observation_days': SmartPowerController.OBSERVATION_DAYS
        }
    
    @staticmethod
    def apply_alpha_beta_cutoff(room, energy_log, reason):
        """
        Apply complete power cutoff (alpha-beta pruning style)
        Sets all loads to zero
        """
        # Store previous state
        previous_state = {
            'base_load': energy_log.base_load,
            'ac_load': energy_log.ac_load,
            'light_load': energy_log.light_load,
            'equipment_load': energy_log.equipment_load,
            'total_load': energy_log.total_load
        }
        
        # Calculate energy that would have been used
        energy_saved = energy_log.total_load
        
        # Apply complete cutoff
        energy_log.base_load = 0.0
        energy_log.ac_load = 0.0
        energy_log.light_load = 0.0
        energy_log.equipment_load = 0.0
        energy_log.total_load = 0.0
        energy_log.optimized = True
        
        new_state = {
            'base_load': 0.0,
            'ac_load': 0.0,
            'light_load': 0.0,
            'equipment_load': 0.0,
            'total_load': 0.0
        }
        
        # Log autonomous action
        auto_log = AutonomousLog(
            timestamp=datetime.now(),
            action_type='POWER_CUTOFF',
            room_id=room.id,
            reason=reason,
            energy_saved_kwh=round(energy_saved / 60, 4),  # Convert to kWh (per minute)
            previous_state=json.dumps(previous_state),
            new_state=json.dumps(new_state),
            is_optimization=True,
            confidence_score=0.85  # Based on historical pattern
        )
        db.session.add(auto_log)
        
        return energy_saved
    
    @staticmethod
    def check_demand_spike(building_id, current_load, previous_load):
        """
        Check if there's a demand spike that requires source switch
        Returns True if load increased by more than threshold
        """
        if previous_load is None:
            return False, 0
        
        load_increase = current_load - previous_load
        
        if load_increase > SmartPowerController.DEMAND_SPIKE_THRESHOLD:
            return True, load_increase
        
        return False, load_increase
    
    @staticmethod
    def switch_to_hybrid_mode(building_id, current_load, solar_capacity, reason):
        """
        Activate hybrid mode (solar + grid) when demand exceeds solar capacity
        """
        sources = {src.name: src for src in EnergySource.query.all()}
        solar_source = sources.get('solar')
        grid_source = sources.get('grid')
        
        if not solar_source or not grid_source:
            return None, "Energy sources not configured"
        
        # Calculate power distribution
        solar_contribution = min(current_load, solar_capacity)
        grid_contribution = max(0, current_load - solar_capacity)
        
        # Get or create power config
        config = PowerSourceConfig.query.filter_by(building_id=building_id).first()
        if not config:
            config = PowerSourceConfig(
                building_id=building_id,
                solar_capacity_kw=SmartPowerController.SOLAR_CAPACITY_PER_BUILDING
            )
            db.session.add(config)
        
        # Update config
        config.hybrid_mode_active = True
        config.current_solar_output_kw = solar_contribution
        config.last_source_switch = datetime.now()
        
        # Log the action
        auto_log = AutonomousLog(
            timestamp=datetime.now(),
            action_type='HYBRID_MODE',
            building_id=building_id,
            reason=reason,
            energy_saved_kwh=0,  # Hybrid mode doesn't save energy, it ensures stability
            previous_state=json.dumps({'mode': 'solar_only', 'load': current_load}),
            new_state=json.dumps({
                'mode': 'hybrid',
                'solar_kw': solar_contribution,
                'grid_kw': grid_contribution
            }),
            is_optimization=True
        )
        db.session.add(auto_log)
        
        return {
            'mode': 'hybrid',
            'solar_contribution_kw': round(solar_contribution, 2),
            'grid_contribution_kw': round(grid_contribution, 2),
            'total_load_kw': round(current_load, 2)
        }, None
    
    @staticmethod
    def calculate_gradual_transition(current_source, target_source, step):
        """
        Calculate gradual transition between power sources
        step: 1-6 (over 30 minutes, 5 min per step)
        Returns: percentage of load on each source
        """
        if step < 1:
            step = 1
        if step > SmartPowerController.TRANSITION_STEPS:
            step = SmartPowerController.TRANSITION_STEPS
        
        # Linear transition
        target_percentage = step / SmartPowerController.TRANSITION_STEPS
        current_percentage = 1 - target_percentage
        
        return {
            current_source: round(current_percentage, 2),
            target_source: round(target_percentage, 2),
            'step': step,
            'total_steps': SmartPowerController.TRANSITION_STEPS,
            'transition_complete': step >= SmartPowerController.TRANSITION_STEPS
        }
    
    @staticmethod
    def predictive_source_switch(building_id, predicted_load_30min, current_load):
        """
        Proactively switch sources based on 30-minute ahead prediction
        """
        current_hour = datetime.now().hour
        solar_availability = SmartPowerController.get_solar_availability(current_hour + 1)  # +1 for prediction
        
        solar_capacity = SmartPowerController.SOLAR_CAPACITY_PER_BUILDING * solar_availability
        
        sources = {src.name: src for src in EnergySource.query.all()}
        
        action_taken = None
        
        # Check if predicted load will exceed solar capacity
        if predicted_load_30min > solar_capacity and solar_availability > 0:
            # Need to start transitioning to hybrid mode
            config = PowerSourceConfig.query.filter_by(building_id=building_id).first()
            
            if config and not config.hybrid_mode_active:
                action_taken = 'PREDICTIVE_SWITCH'
                reason = f"Predicted load ({predicted_load_30min:.1f} kW) will exceed solar capacity ({solar_capacity:.1f} kW) in 30 minutes"
                
                # Log predictive action
                auto_log = AutonomousLog(
                    timestamp=datetime.now(),
                    action_type='PREDICTIVE_SWITCH',
                    building_id=building_id,
                    reason=reason,
                    previous_state=json.dumps({'mode': 'solar_only'}),
                    new_state=json.dumps({'mode': 'transitioning_to_hybrid'}),
                    is_optimization=True,
                    confidence_score=0.75
                )
                db.session.add(auto_log)
                
                return {
                    'action': 'TRANSITION_STARTED',
                    'reason': reason,
                    'predicted_load': predicted_load_30min,
                    'current_capacity': solar_capacity,
                    'recommendation': 'Begin gradual transition to hybrid mode'
                }
        
        # Check if evening transition needed (after 6 PM)
        if current_hour >= 18 and solar_availability < 1.0:
            action_taken = 'EVENING_TRANSITION'
            return {
                'action': 'EVENING_TRANSITION',
                'reason': 'Solar output reducing (evening)',
                'solar_availability': solar_availability,
                'recommendation': 'Transitioning to grid-primary mode'
            }
        
        return None
    
    @staticmethod
    def get_risky_schedules(min_cancellation_rate=0.5):
        """
        Get all room schedules with high cancellation rates
        For dashboard display
        """
        patterns = CancellationPattern.query.filter(
            CancellationPattern.cancellation_rate >= min_cancellation_rate,
            CancellationPattern.scheduled_count >= 5  # At least 5 observations
        ).order_by(CancellationPattern.cancellation_rate.desc()).all()
        
        risky_schedules = []
        for pattern in patterns:
            room = Room.query.get(pattern.room_id)
            if room:
                risky_schedules.append({
                    'room_id': pattern.room_id,
                    'room_name': room.name,
                    'room_type': room.type,
                    'day_of_week': pattern.day_of_week,
                    'hour': pattern.hour,
                    'cancellation_rate': round(pattern.cancellation_rate * 100, 1),
                    'scheduled_count': pattern.scheduled_count,
                    'occupied_count': pattern.occupied_count,
                    'auto_cutoff_enabled': pattern.auto_cutoff_enabled
                })
        
        return risky_schedules
    
    @staticmethod
    def get_prediction_accuracy():
        """
        Calculate historical accuracy of autonomous actions
        """
        # Get logs from last 7 days
        cutoff = datetime.now() - timedelta(days=7)
        
        cutoff_logs = AutonomousLog.query.filter(
            AutonomousLog.action_type == 'POWER_CUTOFF',
            AutonomousLog.timestamp >= cutoff
        ).all()
        
        if not cutoff_logs:
            return {
                'total_predictions': 0,
                'accuracy': None,
                'message': 'No prediction data available'
            }
        
        # For each cutoff, check if room remained unoccupied
        correct_predictions = 0
        for log in cutoff_logs:
            # Check next energy log for this room
            next_log = EnergyLog.query.filter(
                EnergyLog.room_id == log.room_id,
                EnergyLog.timestamp > log.timestamp
            ).order_by(EnergyLog.timestamp).first()
            
            if next_log and not next_log.occupancy:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(cutoff_logs) if cutoff_logs else 0
        
        return {
            'total_predictions': len(cutoff_logs),
            'correct_predictions': correct_predictions,
            'accuracy': round(accuracy * 100, 1),
            'period_days': 7
        }
    
    @staticmethod
    def update_cancellation_pattern(room_id, day_of_week, hour, was_occupied):
        """
        Update cancellation pattern statistics for a room
        Called after each simulation cycle
        """
        # Get or create pattern record
        pattern = CancellationPattern.query.filter_by(
            room_id=room_id,
            day_of_week=day_of_week,
            hour=hour
        ).first()
        
        if not pattern:
            pattern = CancellationPattern(
                room_id=room_id,
                day_of_week=day_of_week,
                hour=hour,
                scheduled_count=0,
                occupied_count=0
            )
            db.session.add(pattern)
        
        # Update counts
        pattern.scheduled_count += 1
        if was_occupied:
            pattern.occupied_count += 1
        
        # Calculate new cancellation rate
        if pattern.scheduled_count > 0:
            pattern.cancellation_rate = 1 - (pattern.occupied_count / pattern.scheduled_count)
        
        # Enable auto-cutoff if threshold exceeded and enough observations
        if (pattern.cancellation_rate >= SmartPowerController.CANCELLATION_THRESHOLD 
            and pattern.scheduled_count >= 7):  # At least 1 week of data
            pattern.auto_cutoff_enabled = True
        
        pattern.last_updated = datetime.now()
        
        return pattern
    
    @staticmethod
    def should_auto_cutoff(room_id, day_of_week, hour):
        """
        Check if auto-cutoff should be applied based on learned patterns
        """
        pattern = CancellationPattern.query.filter_by(
            room_id=room_id,
            day_of_week=day_of_week,
            hour=hour
        ).first()
        
        if pattern and pattern.auto_cutoff_enabled:
            return True, pattern.cancellation_rate
        
        return False, 0.0
