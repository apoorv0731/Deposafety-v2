#!/usr/bin/env python3
"""
Local 3D Gaussian Splatting Pipeline for DepoSafety V2
Processes video locally for small datasets (budget-friendly)
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ThreeDGSProcessor:
    """3D Gaussian Splatting pipeline processor"""
    
    def __init__(self, 
                 video_path: str,
                 output_dir: str,
                 frame_rate: int = 2,
                 resolution: int = -1,
                 iterations: int = 30000,
                 webhook_url: Optional[str] = None,
                 job_id: Optional[str] = None):
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)
        self.frame_rate = frame_rate
        self.resolution = resolution
        self.iterations = iterations
        self.webhook_url = webhook_url
        self.job_id = job_id or os.urandom(8).hex()
        
        # Subdirectories
        self.frames_dir = self.output_dir / "frames"
        self.colmap_dir = self.output_dir / "colmap"
        self.gaussian_dir = self.output_dir / "gaussian"
        self.export_dir = self.output_dir / "export"
        
    def setup_directories(self):
        """Create output directories"""
        for d in [self.frames_dir, self.colmap_dir, self.gaussian_dir, self.export_dir]:
            d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directories in {self.output_dir}")
        
    def extract_frames(self) -> bool:
        """Extract frames from video using ffmpeg"""
        logger.info(f"Extracting frames at {self.frame_rate} fps...")
        
        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-i", str(self.video_path),
            "-vf", f"fps={self.frame_rate}",
            "-q:v", "2",
            str(self.frames_dir / "frame_%04d.jpg")
        ]
        
        # Add resize if specified
        if self.resolution > 0:
            cmd[3] = f"fps={self.frame_rate},scale={self.resolution}:-1"
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            frame_count = len(list(self.frames_dir.glob("*.jpg")))
            logger.info(f"Extracted {frame_count} frames")
            return frame_count > 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Frame extraction failed: {e.stderr}")
            return False
            
    def run_colmap(self) -> bool:
        """Run COLMAP for camera pose estimation"""
        logger.info("Running COLMAP...")
        
        # Feature extraction
        feat_cmd = [
            "colmap", "feature_extractor",
            "--database_path", str(self.colmap_dir / "database.db"),
            "--image_path", str(self.frames_dir),
            "--ImageReader.camera_model", "OPENCV",
            "--ImageReader.single_camera", "1"
        ]
        
        try:
            subprocess.run(feat_cmd, capture_output=True, text=True, check=True)
            logger.info("Feature extraction complete")
        except subprocess.CalledProcessError as e:
            logger.error(f"Feature extraction failed: {e.stderr}")
            return False
            
        # Feature matching
        match_cmd = [
            "colmap", "exhaustive_matcher",
            "--database_path", str(self.colmap_dir / "database.db")
        ]
        
        try:
            subprocess.run(match_cmd, capture_output=True, text=True, check=True)
            logger.info("Feature matching complete")
        except subprocess.CalledProcessError as e:
            logger.error(f"Feature matching failed: {e.stderr}")
            return False
            
        # Sparse reconstruction
        sparse_dir = self.colmap_dir / "sparse"
        sparse_dir.mkdir(exist_ok=True)
        
        mapper_cmd = [
            "colmap", "mapper",
            "--database_path", str(self.colmap_dir / "database.db"),
            "--image_path", str(self.frames_dir),
            "--output_path", str(sparse_dir)
        ]
        
        try:
            subprocess.run(mapper_cmd, capture_output=True, text=True, check=True)
            logger.info("Sparse reconstruction complete")
        except subprocess.CalledProcessError as e:
            logger.error(f"Mapper failed: {e.stderr}")
            return False
            
        # Convert to TXT for gaussian-splatting
        txt_dir = self.colmap_dir / "sparse_txt"
        txt_dir.mkdir(exist_ok=True)
        
        model_converter_cmd = [
            "colmap", "model_converter",
            "--input_path", str(sparse_dir / "0"),
            "--output_path", str(txt_dir),
            "--output_type", "TXT"
        ]
        
        try:
            subprocess.run(model_converter_cmd, capture_output=True, text=True, check=True)
            logger.info("Model conversion complete")
        except subprocess.CalledProcessError as e:
            logger.error(f"Model conversion failed: {e.stderr}")
            return False
            
        return True
        
    def prepare_gaussian_splatting_data(self) -> bool:
        """Prepare data in format expected by gaussian-splatting"""
        logger.info("Preparing data for Gaussian Splatting...")
        
        # Create input structure
        input_dir = self.gaussian_dir / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy frames
        for frame in self.frames_dir.glob("*.jpg"):
            shutil.copy(frame, input_dir / frame.name)
            
        # Copy COLMAP output
        sparse_dst = self.gaussian_dir / "sparse" / "0"
        sparse_dst.mkdir(parents=True, exist_ok=True)
        
        sparse_src = self.colmap_dir / "sparse" / "0"
        for f in sparse_src.glob("*"):
            shutil.copy(f, sparse_dst / f.name)
            
        logger.info("Data preparation complete")
        return True
        
    def train_gaussian_splatting(self) -> bool:
        """Train 3D Gaussian Splatting model"""
        logger.info("Training 3D Gaussian Splatting model...")
        
        # Check if gaussian-splatting repo exists
        gs_repo = Path("gaussian-splatting")
        if not gs_repo.exists():
            logger.error("gaussian-splatting repository not found. Please clone it first.")
            logger.info("Run: git clone --recursive https://github.com/graphdeco-inria/gaussian-splatting.git")
            return False
            
        train_cmd = [
            sys.executable,
            str(gs_repo / "train.py"),
            "-s", str(self.gaussian_dir),
            "-m", str(self.gaussian_dir / "output"),
            "--iterations", str(self.iterations),
            "--save_iterations", "7000", "30000"
        ]
        
        try:
            subprocess.run(train_cmd, check=True)
            logger.info("Training complete")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Training failed: {e}")
            return False
            
    def export_models(self) -> Dict[str, str]:
        """Export PLY and SPLAT files"""
        logger.info("Exporting models...")
        
        output_models = {}
        
        # Find trained model
        model_dir = self.gaussian_dir / "output" / "point_cloud"
        if not model_dir.exists():
            logger.error("No trained model found")
            return output_models
            
        # Get iteration folder
        iter_dirs = list(model_dir.glob("iteration_*"))
        if not iter_dirs:
            logger.error("No iteration folders found")
            return output_models
            
        latest_iter = sorted(iter_dirs)[-1]
        ply_file = latest_iter / "point_cloud.ply"
        
        if ply_file.exists():
            # Copy PLY
            ply_dst = self.export_dir / "model.ply"
            shutil.copy(ply_file, ply_dst)
            output_models['ply'] = str(ply_dst)
            logger.info(f"Exported PLY: {ply_dst}")
            
            # Convert to SPLAT
            splat_file = self.export_dir / "model.splat"
            if self.convert_ply_to_splat(ply_file, splat_file):
                output_models['splat'] = str(splat_file)
                logger.info(f"Exported SPLAT: {splat_file}")
                
        return output_models
        
    def convert_ply_to_splat(self, ply_path: Path, splat_path: Path) -> bool:
        """Convert PLY to compressed SPLAT format"""
        try:
            import numpy as np
            
            # Read PLY file
            from plyfile import PlyData
            plydata = PlyData.read(str(ply_path))
            
            vertex = plydata['vertex']
            x = np.asarray(vertex['x'])
            y = np.asarray(vertex['y'])
            z = np.asarray(vertex['z'])
            
            # Extract Gaussian parameters
            nx = np.asarray(vertex['nx']) if 'nx' in vertex else np.zeros_like(x)
            ny = np.asarray(vertex['ny']) if 'ny' in vertex else np.zeros_like(x)
            nz = np.asarray(vertex['nz']) if 'nz' in vertex else np.zeros_like(x)
            
            # SH coefficients for color
            f_dc = np.stack([
                np.asarray(vertex['f_dc_0']),
                np.asarray(vertex['f_dc_1']),
                np.asarray(vertex['f_dc_2'])
            ], axis=1)
            
            # Convert SH to RGB
            def sigmoid(x):
                return 1 / (1 + np.exp(-x))
            
            colors = sigmoid(f_dc) * 255
            colors = colors.astype(np.uint8)
            
            # Opacity
            opacity = sigmoid(np.asarray(vertex['opacity'])) if 'opacity' in vertex else np.ones_like(x)
            
            # Scale
            scale = np.stack([
                np.exp(np.asarray(vertex['scale_0'])) if 'scale_0' in vertex else np.ones_like(x),
                np.exp(np.asarray(vertex['scale_1'])) if 'scale_1' in vertex else np.ones_like(x),
                np.exp(np.asarray(vertex['scale_2'])) if 'scale_2' in vertex else np.ones_like(x)
            ], axis=1)
            
            # Rotation (quaternion)
            rot = np.stack([
                np.asarray(vertex['rot_0']) if 'rot_0' in vertex else np.ones_like(x),
                np.asarray(vertex['rot_1']) if 'rot_1' in vertex else np.zeros_like(x),
                np.asarray(vertex['rot_2']) if 'rot_2' in vertex else np.zeros_like(x),
                np.asarray(vertex['rot_3']) if 'rot_3' in vertex else np.zeros_like(x)
            ], axis=1)
            
            # Normalize quaternions
            rot_norm = np.linalg.norm(rot, axis=1, keepdims=True)
            rot = rot / (rot_norm + 1e-8)
            
            # Pack into SPLAT format
            # Position (12 bytes) + Scale (12 bytes) + Color (4 bytes) + Rotation (4 bytes)
            num_gaussians = len(x)
            splat_data = np.zeros(num_gaussians, dtype=[
                ('position', np.float32, 3),
                ('scale', np.float32, 3),
                ('color', np.uint8, 4),
                ('rotation', np.uint8, 4)
            ])
            
            splat_data['position'] = np.stack([x, y, z], axis=1)
            splat_data['scale'] = scale
            splat_data['color'] = np.concatenate([colors, (opacity * 255).astype(np.uint8)[:, None]], axis=1)
            
            # Pack quaternion into 4 bytes (each component to uint8)
            rot_uint8 = ((rot + 1) * 127.5).astype(np.uint8)
            splat_data['rotation'] = rot_uint8
            
            # Write SPLAT file
            splat_data.tofile(str(splat_path))
            
            return True
            
        except ImportError:
            logger.warning("plyfile not installed, skipping SPLAT conversion")
            return False
        except Exception as e:
            logger.error(f"SPLAT conversion failed: {e}")
            return False
            
    def notify_webhook(self, status: str, models: Dict[str, str] = None, error: str = None):
        """Notify backend via webhook"""
        if not self.webhook_url:
            return
            
        try:
            from api_client import notify_processing_complete
            notify_processing_complete(
                webhook_url=self.webhook_url,
                job_id=self.job_id,
                status=status,
                models=models,
                error=error
            )
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            
    def run(self) -> bool:
        """Run the complete pipeline"""
        logger.info(f"Starting 3DGS pipeline for job {self.job_id}")
        
        try:
            self.setup_directories()
            
            # Step 1: Extract frames
            if not self.extract_frames():
                self.notify_webhook("failed", error="Frame extraction failed")
                return False
                
            # Step 2: COLMAP
            if not self.run_colmap():
                self.notify_webhook("failed", error="COLMAP failed")
                return False
                
            # Step 3: Prepare data
            if not self.prepare_gaussian_splatting_data():
                self.notify_webhook("failed", error="Data preparation failed")
                return False
                
            # Step 4: Train
            if not self.train_gaussian_splatting():
                self.notify_webhook("failed", error="Training failed")
                return False
                
            # Step 5: Export
            models = self.export_models()
            if not models:
                self.notify_webhook("failed", error="Export failed")
                return False
                
            # Success
            self.notify_webhook("completed", models=models)
            logger.info(f"Pipeline complete! Models: {models}")
            return True
            
        except Exception as e:
            logger.exception("Pipeline failed")
            self.notify_webhook("failed", error=str(e))
            return False


def main():
    parser = argparse.ArgumentParser(description="3D Gaussian Splatting Pipeline")
    parser.add_argument("--video", "-v", required=True, help="Input video path")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    parser.add_argument("--fps", "-f", type=int, default=2, help="Frame extraction rate")
    parser.add_argument("--resolution", "-r", type=int, default=-1, help="Frame resolution (-1 for original)")
    parser.add_argument("--iterations", "-i", type=int, default=30000, help="Training iterations")
    parser.add_argument("--webhook", "-w", help="Webhook URL for notifications")
    parser.add_argument("--job-id", "-j", help="Job ID for tracking")
    
    args = parser.parse_args()
    
    processor = ThreeDGSProcessor(
        video_path=args.video,
        output_dir=args.output,
        frame_rate=args.fps,
        resolution=args.resolution,
        iterations=args.iterations,
        webhook_url=args.webhook,
        job_id=args.job_id
    )
    
    success = processor.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
