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
        scenario = (self.frame_count // 30) % 5
        
        if scenario == 0:
            depth_map[150:250, 250:390] = 762  # center at 2.5 feet
        elif scenario == 1:
            depth_map[100:300, 50:200] = 914  # left at 3 feet
        elif scenario == 2:
            depth_map[100:300, 440:590] = 1067  # right at 3.5 feet
        elif scenario == 3:
            depth_map[150:250, 250:390] = 762
            depth_map[100:200, 50:150] = 1219
        elif scenario == 4:
            depth_map[150:250, 100:200] = 914
            depth_map[120:280, 270:370] = 685
            depth_map[180:280, 450:550] = 1143
        
        noise = np.random.normal(0, 10, depth_map.shape)
        depth_map = depth_map + noise
        
        rgb_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        return {
            'rgb': rgb_frame,
            'depth': depth_map,
            'timestamp': datetime.now().isoformat()
        }
    
    def stop(self):
        """Stop the mock camera"""
        print("Mock camera stopped")
