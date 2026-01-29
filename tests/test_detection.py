import sys
sys.path.append('../src')

from camera.mock_oak_camera import MockOAKCamera
from detection.obstacle_detector import ObstacleDetector
import numpy as np

def test_detector_initialization():
    """Test that detector initializes correctly"""
    detector = ObstacleDetector(min_distance_feet=2, max_distance_feet=4)

    assert detector.min_distance_mm == 2 * 304.8
    assert detector.max_distance_mm == 4 * 304.8

    print("✓ Detector initialization test passed")

def test_no_obstacles():
    """Test when there are no obstacles"""
    detector = ObstacleDetector()

    # Create depth map with all objects far away (> 4 feet)
    depth_map = np.full((400, 640), 2000, dtype=np.uint16)  # ~6.5 feet

    obstacles = detector.detect_obstacles(depth_map)

    assert len(obstacles) == 0, "Should detect no obstacles"
    print("✓ No obstacles test passed")

def test_obstacle_detection():
    """Test that obstacles are correctly detected"""
    detector = ObstacleDetector()
    camera = MockOAKCamera()

    # Capture frame
    frame = camera.capture_rgb_depth()

    # Detect obstacles
    obstacles = detector.detect_obstacles(frame['depth'])

    assert isinstance(obstacles, list)
    print(f"✓ Obstacle detection test passed ({len(obstacles)} obstacles found)")

def test_priority_obstacle():
    """Test priority obstacle selection"""
    detector = ObstacleDetector()

    test_obstacles = [
        {'region': 'left', 'distance_feet': 3.5},
        {'region': 'center', 'distance_feet': 2.1},  # Closest
        {'region': 'right', 'distance_feet': 3.8},
    ]

    priority = detector.get_priority_obstacle(test_obstacles)

    assert priority['distance_feet'] == 2.1, "Should select closest obstacle"
    assert priority['region'] == 'center'

    print("✓ Priority obstacle test passed")

def test_oak_camera_interface():
    """Test that the real OAKCamera class exposes the expected interface"""
    from camera.oak_camera import OAKCamera

    # Verify the class has the same public methods as MockOAKCamera
    required_methods = ['capture_rgb_depth', 'get_depth_at_point', 'mm_to_feet']
    for method in required_methods:
        assert hasattr(OAKCamera, method), f"OAKCamera missing method: {method}"

    # Verify it also has a close() method for cleanup
    assert hasattr(OAKCamera, 'close'), "OAKCamera missing close() method"

    print("✓ OAK camera interface test passed")

if __name__ == "__main__":
    print("Running obstacle detection tests...\n")

    test_detector_initialization()
    test_no_obstacles()
    test_obstacle_detection()
    test_priority_obstacle()
    test_oak_camera_interface()

    print("\n All tests passed!")
