import numpy as np
import cv2
import time
from datetime import datetime

class MockOAKCamera:
    """Simulates OAK FFC 3P camera with depth sensing"""
    
    def __init__(self, width=640, height=400):
        self.width = width
        self.height = height
        self.fps = 30
        
    def capture_rgb_depth(self):
        """
        Simulates RGB + Depth capture
        Returns: (rgb_frame, depth_map)
        """
        # Create mock RGB frame (grayscale for now)
        rgb_frame = np.random.randint(0, 255, (self.height, self.width, 3), dtype=np.uint8)
        
        # Create mock depth map (in millimeters)
        # Simulate objects at different distances (500mm to 4000mm = 0.5 to 4 feet)
        depth_map = np.random.randint(500, 4000, (self.height, self.width), dtype=np.uint16)
        
        # Add some "objects" at specific distances
        # Object 1: Close obstacle (2 feet = 600mm)
        depth_map[100:200, 200:300] = 600
        
        # Object 2: Medium distance (3 feet = 900mm)
        depth_map[150:250, 350:450] = 900
        
        timestamp = datetime.now().isoformat()
        
        return {
            'rgb': rgb_frame,
            'depth': depth_map,
            'timestamp': timestamp
        }
    
    def get_depth_at_point(self, x, y, depth_map):
        """Get depth value at specific pixel coordinates"""
        return depth_map[y, x]
    
    def mm_to_feet(self, mm):
        """Convert millimeters to feet"""
        return mm / 304.8
    
    def simulate_continuous_capture(self, duration_seconds=10):
        """Simulate continuous capture like real camera"""
        frames = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            frame_data = self.capture_rgb_depth()
            frames.append(frame_data)
            time.sleep(1/self.fps)  # Simulate 30 FPS
        
        return frames


# Example usage
if __name__ == "__main__":
    camera = MockOAKCamera()
    
    print("Capturing single frame...")
    frame = camera.capture_rgb_depth()
    
    print(f"RGB shape: {frame['rgb'].shape}")
    print(f"Depth shape: {frame['depth'].shape}")
    print(f"Timestamp: {frame['timestamp']}")
    
    # Check depth at center point
    center_x, center_y = 320, 200
    depth_mm = camera.get_depth_at_point(center_x, center_y, frame['depth'])
    depth_feet = camera.mm_to_feet(depth_mm)
    
    print(f"\nDepth at center ({center_x}, {center_y}): {depth_mm}mm ({depth_feet:.2f} feet)")