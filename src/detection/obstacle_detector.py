import numpy as np
from datetime import datetime
import time

class ObstacleDetector:
    """Detects obstacles within specified range (2-4 feet)"""
    
    def __init__(self, min_distance_feet=2, max_distance_feet=6):
        self.min_distance_mm = min_distance_feet * 304.8
        self.max_distance_mm = max_distance_feet * 304.8
        self.detection_threshold = 0.1  # 10% of frame must contain obstacle
        
    def detect_obstacles(self, depth_map):
        """
        Analyze depth map for obstacles in danger zone (2-4 feet)
        Returns: List of detected obstacles with positions and distances
        """
        obstacles = []
        
        # Find pixels within danger zone
        danger_zone = (depth_map >= self.min_distance_mm) & (depth_map <= self.max_distance_mm)
        
        if np.sum(danger_zone) == 0:
            return obstacles  # No obstacles detected
        
        # Divide frame into regions (left, center, right)
        height, width = depth_map.shape
        regions = {
            'left': depth_map[:, :width//3],
            'center': depth_map[:, width//3:2*width//3],
            'right': depth_map[:, 2*width//3:]
        }
        
        for region_name, region_data in regions.items():
            # Check if this region has obstacles
            region_danger = (region_data >= self.min_distance_mm) & (region_data <= self.max_distance_mm)
            
            if np.sum(region_danger) > (region_data.size * self.detection_threshold):
                # Calculate average distance of obstacles in this region
                obstacle_depths = region_data[region_danger]
                avg_distance_mm = np.mean(obstacle_depths)
                avg_distance_feet = avg_distance_mm / 304.8
                
                obstacle = {
                    'region': region_name,
                    'distance_feet': round(avg_distance_feet, 1),
                    'distance_mm': int(avg_distance_mm),
                    'coverage_percent': round(np.sum(region_danger) / region_data.size * 100, 1),
                    'timestamp': datetime.now().isoformat()
                }
                
                obstacles.append(obstacle)
        
        return obstacles
    
    def get_priority_obstacle(self, obstacles):
        """Return the closest/most dangerous obstacle"""
        if not obstacles:
            return None
        
        # Sort by distance (closest first)
        sorted_obstacles = sorted(obstacles, key=lambda x: x['distance_feet'])
        return sorted_obstacles[0]


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from camera.real_oak_camera import RealOAKCamera
    
    camera = RealOAKCamera()
    camera.start()
    detector = ObstacleDetector(min_distance_feet=2, max_distance_feet=4)
    
    print("Testing obstacle detection...\n")
    
    for i in range(5):
        # Capture frame
        frame = camera.capture_rgb_depth()
        
        # Detect obstacles
        obstacles = detector.detect_obstacles(frame['depth'])
        
        print(f"Frame {i+1}:")
        if obstacles:
            for obs in obstacles:
                print(f"  - {obs['region'].upper()}: {obs['distance_feet']} feet "
                      f"(coverage: {obs['coverage_percent']}%)")
            
            priority = detector.get_priority_obstacle(obstacles)
            print(f"    PRIORITY: {priority['region']} at {priority['distance_feet']} feet")
        else:
            print("   No obstacles detected")
        
        print()
        time.sleep(0.5)
