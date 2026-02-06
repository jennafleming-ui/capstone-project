import subprocess
import time
from datetime import datetime

class AudioFeedbackGenerator:
    """Generates real-time audio warnings for obstacles using espeak directly"""
    
    def __init__(self):
        # Track last announcement to avoid repetition
        self.last_announcement = None
        self.announcement_cooldown = 2.0
        self.last_announcement_time = 0
        
    def generate_obstacle_warning(self, obstacle):
        """Generate audio warning for detected obstacle"""
        if obstacle is None:
            return None
        
        region = obstacle['region']
        distance = obstacle['distance_feet']
        
        # Create warning message
        if distance < 2.5:
            urgency = "Caution"
        elif distance < 3.5:
            urgency = "Warning"
        else:
            urgency = "Notice"
        
        message = f"{urgency}. {region} obstacle at {distance} feet"
        return message
    
    def speak(self, message, force=False):
        """Speak the message using espeak directly"""
        current_time = time.time()
        
        # Check cooldown
        if not force and (current_time - self.last_announcement_time) < self.announcement_cooldown:
            if message == self.last_announcement:
                return False
        
        print(f"[AUDIO] {message}")
        
        # Use espeak directly - no pyttsx3
        try:
            subprocess.run(['espeak', message], check=False)
        except Exception as e:
            print(f"Audio error: {e}")
        
        self.last_announcement = message
        self.last_announcement_time = current_time
        return True
    
    def generate_and_speak(self, obstacles):
        """Generate and speak warnings for all obstacles"""
        if not obstacles:
            return
        
        # Get priority obstacle (closest)
        priority = sorted(obstacles, key=lambda x: x['distance_feet'])[0]
        warning = self.generate_obstacle_warning(priority)
        self.speak(warning)


# Example usage
if __name__ == "__main__":
    audio = AudioFeedbackGenerator()
    
    test_obstacles = [
        {'region': 'center', 'distance_feet': 2.1},
        {'region': 'left', 'distance_feet': 3.5},
        {'region': 'right', 'distance_feet': 3.8},
    ]
    
    print("Testing audio feedback...\n")
    
    for obstacle in test_obstacles:
        warning = audio.generate_obstacle_warning(obstacle)
        print(f"Obstacle: {obstacle}")
        print(f"Warning: {warning}\n")
        audio.speak(warning, force=True)
        time.sleep(1)
