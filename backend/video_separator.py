import os
from pathlib import Path
import cv2
from typing import Dict, Optional

class VideoSeparator:
    def __init__(self, input_path: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize video separator
        
        Args:
            input_path: Input video path, if None then use default path
            output_dir: Output directory path, if None then use default path
        """
        self.base_path = Path(__file__).parent
        self.input_path = input_path
        self.output_dir = output_dir or str(self.base_path / "separated_videos")
        
    def _setup_output_dir(self):
        """Create output directory"""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _get_video_info(self, cap: cv2.VideoCapture) -> Dict:
        """Get video information"""
        return {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }
        
    def _create_writers(self, video_info: Dict) -> list:
        """Create video writers"""
        w_sub = video_info["width"] // 4
        h_sub = video_info["height"]
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        
        writers = []
        for i in range(4):
            out_name = f"{base_name}_cam{i+1}.mp4"
            out_path = os.path.join(self.output_dir, out_name)
            
            # The second video needs to be rotated 90 degrees
            if i == 1:
                writers.append(cv2.VideoWriter(out_path, fourcc, video_info["fps"], (h_sub, w_sub)))
            else:
                writers.append(cv2.VideoWriter(out_path, fourcc, video_info["fps"], (w_sub, h_sub)))
                
        return writers
        
    def separate_video(self) -> Dict[str, str]:
        """
        Separate video into four perspectives
        
        Returns:
            Dict[str, str]: Dictionary containing paths to four perspectives videos
        """
        self._setup_output_dir()
        
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video file: {self.input_path}")
            
        try:
            video_info = self._get_video_info(cap)
            writers = self._create_writers(video_info)
            w_sub = video_info["width"] // 4
            
            # Process each frame
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                for i, writer in enumerate(writers):
                    x0 = i * w_sub
                    roi = frame[0:video_info["height"], x0:x0 + w_sub]
                    
                    if i == 1:
                        roi = cv2.rotate(roi, cv2.ROTATE_90_CLOCKWISE)
                        
                    writer.write(roi)
                    
        finally:
            # Release resources
            cap.release()
            for writer in writers:
                writer.release()
                
        # Return separated video paths
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        return {
            "top": str(Path(self.output_dir) / f"{base_name}_cam1.mp4"),
            "front": str(Path(self.output_dir) / f"{base_name}_cam2.mp4"),
            "right": str(Path(self.output_dir) / f"{base_name}_cam3.mp4"),
            "left": str(Path(self.output_dir) / f"{base_name}_cam4.mp4")
        }

def separate_video(input_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Convenient function to separate video
    
    Args:
        input_path: Input video path
        output_dir: Output directory path
        
    Returns:
        Dict[str, str]: Dictionary containing paths to four perspectives videos
    """
    separator = VideoSeparator(input_path, output_dir)
    return separator.separate_video() 