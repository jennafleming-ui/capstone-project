import depthai as dai
import numpy as np
import cv2
from datetime import datetime


class OAKCamera:
    """Real OAK FFC 3P camera with RGB and stereo depth sensing"""

    def __init__(self, width=640, height=400, fps=30):
        self.width = width
        self.height = height
        self.fps = fps

        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.depth_queue = None

        self._build_pipeline()
        self._start_device()

    def _build_pipeline(self):
        """Build the DepthAI pipeline for RGB + stereo depth"""
        self.pipeline = dai.Pipeline()

        # RGB camera node
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(self.width, self.height)
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(self.fps)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

        # Mono cameras for stereo depth
        mono_left = self.pipeline.create(dai.node.MonoCamera)
        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        mono_left.setFps(self.fps)

        mono_right = self.pipeline.create(dai.node.MonoCamera)
        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        mono_right.setFps(self.fps)

        # Stereo depth node
        stereo = self.pipeline.create(dai.node.StereoDepth)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
        stereo.setOutputSize(self.width, self.height)
        stereo.setLeftRightCheck(True)
        stereo.setSubpixel(False)

        # Link mono cameras to stereo node
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)

        # Output streams
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)

        xout_depth = self.pipeline.create(dai.node.XLinkOut)
        xout_depth.setStreamName("depth")
        stereo.depth.link(xout_depth.input)

    def _start_device(self):
        """Connect to the OAK device and start the pipeline"""
        self.device = dai.Device(self.pipeline)
        self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.depth_queue = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        print("OAK camera connected and streaming")

    def capture_rgb_depth(self):
        """
        Capture a synchronized RGB + Depth frame from the camera.
        Returns dict with 'rgb', 'depth', and 'timestamp' keys,
        matching the same interface as MockOAKCamera.
        """
        rgb_packet = self.rgb_queue.get()
        depth_packet = self.depth_queue.get()

        rgb_frame = rgb_packet.getCvFrame()                # (H, W, 3) uint8
        depth_map = depth_packet.getFrame().astype(np.uint16)  # (H, W) uint16, millimeters

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

    def close(self):
        """Release the OAK device"""
        if self.device is not None:
            self.device.close()
            self.device = None
            print("OAK camera closed")


# Example usage
if __name__ == "__main__":
    camera = OAKCamera()

    try:
        print("Capturing single frame...")
        frame = camera.capture_rgb_depth()

        print(f"RGB shape: {frame['rgb'].shape}")
        print(f"Depth shape: {frame['depth'].shape}")
        print(f"Timestamp: {frame['timestamp']}")

        center_x, center_y = 320, 200
        depth_mm = camera.get_depth_at_point(center_x, center_y, frame['depth'])
        depth_feet = camera.mm_to_feet(depth_mm)

        print(f"\nDepth at center ({center_x}, {center_y}): {depth_mm}mm ({depth_feet:.2f} feet)")
    finally:
        camera.close()
