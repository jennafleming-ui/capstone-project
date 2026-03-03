import numpy as np
import time
from datetime import datetime

class MockOAKCamera:
    """Mock camera that simulates realistic obstacle scenarios"""
    
    def __init__(self, width=640, height=400):
        self.width = width
        self.height = height
        self.frame_count = 0
        
    def start(self):
        """Start the mock camera"""
        print("Mock Camera started (simulating realistic scenarios)!")
        
    def capture_rgb_depth(self):
        """Generate realistic depth data with obstacles at varying distances"""
        self.frame_count += 1
        
        # Create base depth map (everything at ~10 feet / 3048mm)
        depth_map = np.full((self.height, self.width), 3048.0, dtype=np.float32)
        
        # Simulate different obstacle scenarios based on frame count
        scenario = (self.frame_count // 30) % 5  # Change scenario every 3 seconds
        
        if scenario == 0:
            # CENTER obstacle at 2.5 feet
            depth_map[150:250, 250:390] = 762  # 2.5 feet in mm
            
        elif scenario == 1:
            # LEFT obstacle at 3 feet
            depth_map[100:300, 50:200] = 914  # 3 feet in mm
            
        elif scenario == 2:
            # RIGHT obstacle at 3.5 feet
            depth_map[100:300, 440:590] = 1067  # 3.5 feet in mm
            
        elif scenario == 3:
            # Multiple obstacles - center and left
            depth_map[150:250, 250:390] = 762   # center at 2.5 feet
            depth_map[100:200, 50:150] = 1219   # left at 4 feet
            
        elif scenario == 4:
            # All three regions with obstacles
            depth_map[150:250, 100:200] = 914   # left at 3 feet
            depth_map[120:280, 270:370] = 685   # center at 2.25 feet (close!)
            depth_map[180:280, 450:550] = 1143  # right at 3.75 feet
        
        # Add some realistic noise
        noise = np.random.normal(0, 10, depth_map.shape)
        depth_map = depth_map + noise
        
        # Create dummy RGB frame
        rgb_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        return {
            'rgb': rgb_frame,
            'depth': depth_map,
            'timestamp': datetime.now().isoformat()
        }
    
    def stop(self):
        """Stop the mock camera"""
        print("Mock camera stopped")
