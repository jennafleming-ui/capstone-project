import time
import sys
sys.path.append('.')

TEST_MODE = False

if TEST_MODE:
    from camera.mock_oak_camera import MockOAKCamera as CameraClass
    print(" RUNNING IN TEST MODE - Using Mock Camera\n")
else:
    from camera.real_oak_camera import RealOAKCamera as CameraClass
    print(" Running with Real Oak Camera\n")

from detection.obstacle_detector import ObstacleDetector
from audio.audio_generator import AudioFeedbackGenerator

class AssistiveNavigationSystem:
    """Main system that integrates all components"""
    
    def __init__(self):
        print("Initializing Assistive Navigation Hat System...")
        
        self.camera = CameraClass(width=640, height=400)
        self.camera.start()
        self.detector = ObstacleDetector(min_distance_feet=2, max_distance_feet=6)
        self.audio = AudioFeedbackGenerator()
        
        self.running = False
        self.frame_count = 0
        self.detection_count = 0
        
        print("✓ System initialized\n")
    
    def process_frame(self):
        """Process single frame through the pipeline"""
        # Step 1: Capture from camera
        frame_data = self.camera.capture_rgb_depth()
        
        # Step 2: Detect obstacles
        obstacles = self.detector.detect_obstacles(frame_data['depth'])
        
        # Step 3: Generate audio feedback
        if obstacles:
            self.detection_count += 1
            self.audio.generate_and_speak(obstacles)
        
        self.frame_count += 1
        
        return obstacles
    
    def run(self, duration_seconds=30):
        """Run the system for specified duration"""
        print(f"Starting navigation assistance for {duration_seconds} seconds...")
        print("=" * 50)
        
        self.running = True
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration_seconds and self.running:
                obstacles = self.process_frame()
                
                # Display status every 10 frames
                if self.frame_count % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"\n[{elapsed:.1f}s] Frame {self.frame_count}")
                    print(f"Obstacles detected: {len(obstacles)}")

                    if obstacles:
                        for i, obs in enumerate(obstacles, 1):
                            print(f" Obstacle {i}: Region={obs['region']}, "
                                  f"Distance={obs['distance_feet']:.1f} ft, "
                                  f"Coverage={obs['coverage_percent']:.1f}%")
                
                time.sleep(0.1)  # Simulate processing time
        
        except KeyboardInterrupt:
            print("\n\nSystem stopped by user")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the system and display statistics"""
        self.running = False
        self.camera.stop()
        
        print("\n" + "=" * 50)
        print("System Statistics:")
        print(f"  Total frames processed: {self.frame_count}")
        print(f"  Frames with detections: {self.detection_count}")
        if self.frame_count > 0:
             print(f"  Detection rate: {self.detection_count/self.frame_count*100:.1f}%")
        print("\n✓ System stopped safely")


# Main execution
if __name__ == "__main__":
    system = AssistiveNavigationSystem()
    
    # Run for 30 seconds
    system.run(duration_seconds=float('inf'))
