import numpy as np
import cv2
import time
from datetime import datetime
import depthai as dai

class RealOAKCamera:
    """Uses real OAK camera with depth sensing"""
    
    def __init__(self, width=640, height=400):
        self.width = width
        self.height = height
        self.fps = 30
        
        # Set up the OAK camera pipeline
        self.pipeline = dai.Pipeline()
        
        # RGB camera
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(self.width, self.height)
        cam_rgb.setInterleaved(False)
        
        # Depth cameras (left and right)
        cam_left = self.pipeline.create(dai.node.MonoCamera)
        cam_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        cam_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
        
        cam_right = self.pipeline.create(dai.node.MonoCamera)
        cam_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        cam_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
        
        # Stereo depth
        stereo = self.pipeline.create(dai.node.StereoDepth)
        cam_left.out.link(stereo.left)
        cam_right.out.link(stereo.right)
        
        # Outputs
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)
        
        xout_depth = self.pipeline.create(dai.node.XLinkOut)
        xout_depth.setStreamName("depth")
        stereo.depth.link(xout_depth.input)
    
    def start(self):
        """Start the camera"""
        self.device = dai.Device(self.pipeline)
        self.rgb_out = self.device.getOutputQueue("rgb")
        self.depth_out = self.device.getOutputQueue("depth")
        print("OAK Camera started!")
    
    def capture_rgb_depth(self):
        """Capture real RGB + Depth frame"""
        rgb_frame = self.rgb_out.get().getCvFrame()
        depth_map = self.depth_out.get().getFrame()
        
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
    
    def stop(self):
        """Stop the camera"""
        self.device.close()


# Example usage
if __name__ == "__main__":
    camera = RealOAKCamera()
    camera.start()
    
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
    
    camera.stop()
