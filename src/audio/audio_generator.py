import pyttsx3
import time
from datetime import datetime

class AudioFeedbackGenerator:
    """Generates real-time audio warnings for obstacles"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        try:
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > 0:
                self.engine.setProperty('voice', voices[0].id)
                print(f"Using voice: {voices[0].id}")
        except Exception as e:
            print(f"Voice setting failed, using default: {e}")
            
        self.engine.setProperty('rate', 175)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Track last announcement to avoid repetition
        self.last_announcement = None
        self.announcement_cooldown = 2.0  # seconds
        self.last_announcement_time = 0
        
    def generate_obstacle_warning(self, obstacle):
        """
        Generate audio warning for detected obstacle
        Format: "[Region] obstacle at [X] feet"
        """
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
        """
        Speak the message
        force=True will bypass cooldown
        """
        current_time = time.time()
        
        # Check cooldown (avoid announcement spam)
        if not force and (current_time - self.last_announcement_time) < self.announcement_cooldown:
            if message == self.last_announcement:
                return False  # Skip repeated announcement
        
        print(f"[AUDIO] {message}")
        self.engine.say(message)
        self.engine.runAndWait()
        
        self.last_announcement = message
        self.last_announcement_time = current_time
        
        return True
    
    def generate_and_speak(self, obstacles):
        """Generate and speak warnings for all obstacles"""
        if not obstacles:
            return
        
        # Get priority obstacle (closest)
        priority = sorted(obstacles, key=lambda x: x['distance_feet'])[0]
        
        # Generate warning
        warning = self.generate_obstacle_warning(priority)
        
        # Speak it
        self.speak(warning)


# Example usage
if __name__ == "__main__":
    audio = AudioFeedbackGenerator()
    
    # Test different obstacle scenarios
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
