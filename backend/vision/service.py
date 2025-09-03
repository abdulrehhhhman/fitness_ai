
import cv2
import mediapipe as mp
import numpy as np
import math
import time
from typing import List, Dict, Tuple, Optional, Any
from .schema import (
    ExerciseAnalysisResult, RepetitionData, PlankData, 
    FormFeedback, FrameAnalysis, PoseKeypoint
)

class VisionService:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Exercise-specific parameters
        self.exercise_configs = {
            "squats": {
                "key_angles": ["left_knee", "right_knee", "left_hip", "right_hip"],
                "rep_threshold_down": 90,  # degrees - squat down position
                "rep_threshold_up": 160,   # degrees - standing position
                "form_checks": ["knee_alignment", "back_straight", "depth"]
            },
            "pushups": {
                "key_angles": ["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
                "rep_threshold_down": 90,  # degrees - push-up down position
                "rep_threshold_up": 160,   # degrees - up position
                "form_checks": ["elbow_angle", "body_straight", "head_position"]
            },
            "lunges": {
                "key_angles": ["left_knee", "right_knee", "left_hip", "right_hip"],
                "rep_threshold_down": 90,  # degrees - lunge down position
                "rep_threshold_up": 160,   # degrees - standing position
                "form_checks": ["knee_over_ankle", "back_straight", "depth"]
            },
            "planks": {
                "key_angles": ["left_elbow", "right_elbow", "back_angle"],
                "hold_threshold": 170,     # degrees - straight line threshold
                "form_checks": ["back_straight", "hip_alignment", "head_position"]
            }
        }
    
    def calculate_angle(self, point1: Tuple[float, float], point2: Tuple[float, float], point3: Tuple[float, float]) -> float:
        """Calculate angle between three points"""
        try:
            # Convert to numpy arrays
            a = np.array(point1)
            b = np.array(point2)
            c = np.array(point3)
            
            # Calculate vectors
            ba = a - b
            bc = c - b
            
            # Calculate angle using dot product
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
            angle = np.arccos(cosine_angle)
            
            return math.degrees(angle)
        except:
            return 0.0
    
    def extract_keypoints(self, landmarks) -> Dict[str, PoseKeypoint]:
        """Extract key pose landmarks"""
        keypoints = {}
        
        # Define key landmarks for exercises
        key_landmarks = {
            'left_shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'left_elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': self.mp_pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': self.mp_pose.PoseLandmark.RIGHT_WRIST,
            'left_hip': self.mp_pose.PoseLandmark.LEFT_HIP,
            'right_hip': self.mp_pose.PoseLandmark.RIGHT_HIP,
            'left_knee': self.mp_pose.PoseLandmark.LEFT_KNEE,
            'right_knee': self.mp_pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE,
            'nose': self.mp_pose.PoseLandmark.NOSE
        }
        
        for name, landmark_id in key_landmarks.items():
            landmark = landmarks.landmark[landmark_id]
            keypoints[name] = PoseKeypoint(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility
            )
        
        return keypoints
    
    def calculate_exercise_angles(self, keypoints: Dict[str, PoseKeypoint], exercise_type: str) -> Dict[str, float]:
        """Calculate key angles for specific exercise"""
        angles = {}
        
        try:
            if exercise_type == "squats":
                # Knee angles
                angles['left_knee'] = self.calculate_angle(
                    (keypoints['left_hip'].x, keypoints['left_hip'].y),
                    (keypoints['left_knee'].x, keypoints['left_knee'].y),
                    (keypoints['left_ankle'].x, keypoints['left_ankle'].y)
                )
                angles['right_knee'] = self.calculate_angle(
                    (keypoints['right_hip'].x, keypoints['right_hip'].y),
                    (keypoints['right_knee'].x, keypoints['right_knee'].y),
                    (keypoints['right_ankle'].x, keypoints['right_ankle'].y)
                )
                # Hip angles
                angles['left_hip'] = self.calculate_angle(
                    (keypoints['left_shoulder'].x, keypoints['left_shoulder'].y),
                    (keypoints['left_hip'].x, keypoints['left_hip'].y),
                    (keypoints['left_knee'].x, keypoints['left_knee'].y)
                )
                
            elif exercise_type == "pushups":
                # Elbow angles
                angles['left_elbow'] = self.calculate_angle(
                    (keypoints['left_shoulder'].x, keypoints['left_shoulder'].y),
                    (keypoints['left_elbow'].x, keypoints['left_elbow'].y),
                    (keypoints['left_wrist'].x, keypoints['left_wrist'].y)
                )
                angles['right_elbow'] = self.calculate_angle(
                    (keypoints['right_shoulder'].x, keypoints['right_shoulder'].y),
                    (keypoints['right_elbow'].x, keypoints['right_elbow'].y),
                    (keypoints['right_wrist'].x, keypoints['right_wrist'].y)
                )
                # Body alignment
                angles['body_angle'] = self.calculate_angle(
                    (keypoints['left_shoulder'].x, keypoints['left_shoulder'].y),
                    (keypoints['left_hip'].x, keypoints['left_hip'].y),
                    (keypoints['left_ankle'].x, keypoints['left_ankle'].y)
                )
                
            elif exercise_type == "lunges":
                # Front knee angle (assume left leg is front)
                angles['front_knee'] = self.calculate_angle(
                    (keypoints['left_hip'].x, keypoints['left_hip'].y),
                    (keypoints['left_knee'].x, keypoints['left_knee'].y),
                    (keypoints['left_ankle'].x, keypoints['left_ankle'].y)
                )
                # Back knee angle
                angles['back_knee'] = self.calculate_angle(
                    (keypoints['right_hip'].x, keypoints['right_hip'].y),
                    (keypoints['right_knee'].x, keypoints['right_knee'].y),
                    (keypoints['right_ankle'].x, keypoints['right_ankle'].y)
                )
                
            elif exercise_type == "planks":
                # Back straight angle
                angles['back_angle'] = self.calculate_angle(
                    (keypoints['left_shoulder'].x, keypoints['left_shoulder'].y),
                    (keypoints['left_hip'].x, keypoints['left_hip'].y),
                    (keypoints['left_ankle'].x, keypoints['left_ankle'].y)
                )
                # Elbow angles for plank support
                angles['left_elbow'] = self.calculate_angle(
                    (keypoints['left_shoulder'].x, keypoints['left_shoulder'].y),
                    (keypoints['left_elbow'].x, keypoints['left_elbow'].y),
                    (keypoints['left_wrist'].x, keypoints['left_wrist'].y)
                )
                
        except Exception as e:
            print(f"Error calculating angles: {e}")
        
        return angles
    
    def analyze_form(self, keypoints: Dict[str, PoseKeypoint], angles: Dict[str, float], exercise_type: str) -> Tuple[float, List[str]]:
        """Analyze exercise form and provide feedback"""
        feedback = []
        form_score = 1.0
        
        if exercise_type == "squats":
            # Check knee alignment
            if 'left_knee' in angles and 'right_knee' in angles:
                knee_diff = abs(angles['left_knee'] - angles['right_knee'])
                if knee_diff > 15:
                    feedback.append("Keep knees aligned")
                    form_score -= 0.2
            
            # Check depth
            avg_knee_angle = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
            if avg_knee_angle > 120:
                feedback.append("Squat deeper for better range of motion")
                form_score -= 0.1
            elif avg_knee_angle < 70:
                feedback.append("Don't squat too deep")
                form_score -= 0.1
                
            # Check back position
            if keypoints['left_shoulder'].y > keypoints['left_hip'].y:
                feedback.append("Keep chest up and back straight")
                form_score -= 0.2
        
        elif exercise_type == "pushups":
            # Check elbow alignment
            if 'left_elbow' in angles and 'right_elbow' in angles:
                elbow_diff = abs(angles['left_elbow'] - angles['right_elbow'])
                if elbow_diff > 20:
                    feedback.append("Keep elbows aligned")
                    form_score -= 0.2
            
            # Check body alignment
            if 'body_angle' in angles:
                if angles['body_angle'] < 160:
                    feedback.append("Keep body straight - no sagging hips")
                    form_score -= 0.3
                elif angles['body_angle'] > 190:
                    feedback.append("Lower your hips")
                    form_score -= 0.2
        
        elif exercise_type == "lunges":
            # Check front knee position
            if 'front_knee' in angles:
                if angles['front_knee'] < 80:
                    feedback.append("Don't let front knee go too far forward")
                    form_score -= 0.2
                elif angles['front_knee'] > 110:
                    feedback.append("Lunge deeper for better activation")
                    form_score -= 0.1
        
        elif exercise_type == "planks":
            # Check back alignment
            if 'back_angle' in angles:
                if angles['back_angle'] < 160:
                    feedback.append("Straighten your back")
                    form_score -= 0.3
                elif angles['back_angle'] > 190:
                    feedback.append("Don't arch your back")
                    form_score -= 0.2
            
            # Check hip position
            if keypoints['left_hip'].y < keypoints['left_shoulder'].y:
                feedback.append("Lower your hips")
                form_score -= 0.2
        
        form_score = max(0.0, form_score)
        return form_score, feedback
    
    def count_repetitions(self, exercise_type: str, angles: Dict[str, float], previous_state: Dict) -> Tuple[bool, Dict]:
        """Count repetitions based on exercise-specific logic"""
        config = self.exercise_configs[exercise_type]
        new_rep = False
        
        if exercise_type in ["squats", "pushups", "lunges"]:
            # Get primary angle for rep counting
            if exercise_type == "squats":
                primary_angle = (angles.get('left_knee', 180) + angles.get('right_knee', 180)) / 2
            elif exercise_type == "pushups":
                primary_angle = (angles.get('left_elbow', 180) + angles.get('right_elbow', 180)) / 2
            elif exercise_type == "lunges":
                primary_angle = angles.get('front_knee', 180)
            
            # State machine for rep counting
            if previous_state.get('position') == 'up' and primary_angle < config['rep_threshold_down']:
                previous_state['position'] = 'down'
            elif previous_state.get('position') == 'down' and primary_angle > config['rep_threshold_up']:
                previous_state['position'] = 'up'
                new_rep = True
            elif 'position' not in previous_state:
                previous_state['position'] = 'up' if primary_angle > config['rep_threshold_up'] else 'down'
        
        return new_rep, previous_state
    
    def is_plank_position(self, angles: Dict[str, float]) -> bool:
        """Check if person is in correct plank position"""
        back_angle = angles.get('back_angle', 0)
        return back_angle > 160 and back_angle < 190
    
    def analyze_video_file(self, video_path: str, exercise_type: str) -> ExerciseAnalysisResult:
        """Analyze uploaded video file"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Analysis variables
        frame_count = 0
        poses_detected = 0
        repetitions = []
        plank_sessions = []
        form_feedback = []
        
        rep_count = 0
        rep_state = {}
        plank_start_time = None
        current_plank_feedback = []
        
        form_scores = []
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            timestamp = frame_count / fps
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                poses_detected += 1
                keypoints = self.extract_keypoints(results.pose_landmarks)
                angles = self.calculate_exercise_angles(keypoints, exercise_type)
                form_score, feedback = self.analyze_form(keypoints, angles, exercise_type)
                form_scores.append(form_score)
                
                # Add timestamped feedback
                if feedback:
                    for fb in feedback:
                        form_feedback.append(FormFeedback(
                            timestamp=timestamp,
                            message=fb,
                            severity="warning" if form_score < 0.7 else "info"
                        ))
                
                if exercise_type != "planks":
                    # Count repetitions
                    new_rep, rep_state = self.count_repetitions(exercise_type, angles, rep_state)
                    if new_rep:
                        rep_count += 1
                        repetitions.append(RepetitionData(
                            rep_number=rep_count,
                            timestamp=timestamp,
                            form_quality=form_score,
                            feedback=feedback
                        ))
                else:
                    # Handle plank timing
                    in_plank = self.is_plank_position(angles)
                    if in_plank and plank_start_time is None:
                        plank_start_time = timestamp
                        current_plank_feedback = []
                    elif not in_plank and plank_start_time is not None:
                        duration = timestamp - plank_start_time
                        plank_sessions.append(PlankData(
                            start_time=plank_start_time,
                            end_time=timestamp,
                            duration=duration,
                            form_quality=np.mean(form_scores[-10:]) if form_scores else 0.5,
                            feedback=list(set(current_plank_feedback))
                        ))
                        plank_start_time = None
                    
                    if in_plank:
                        current_plank_feedback.extend(feedback)
        
        # Handle ongoing plank at end of video
        if exercise_type == "planks" and plank_start_time is not None:
            duration = (frame_count / fps) - plank_start_time
            plank_sessions.append(PlankData(
                start_time=plank_start_time,
                end_time=frame_count / fps,
                duration=duration,
                form_quality=np.mean(form_scores[-10:]) if form_scores else 0.5,
                feedback=list(set(current_plank_feedback))
            ))
        
        cap.release()
        
        # Calculate final metrics
        avg_form_score = np.mean(form_scores) if form_scores else 0.0
        total_plank_time = sum(session.duration for session in plank_sessions)
        best_rep_quality = max([rep.form_quality for rep in repetitions]) if repetitions else None
        
        # Generate overall feedback
        overall_feedback = []
        if avg_form_score > 0.8:
            overall_feedback.append("Excellent form overall!")
        elif avg_form_score > 0.6:
            overall_feedback.append("Good form with room for improvement")
        else:
            overall_feedback.append("Focus on form - quality over quantity")
        
        if exercise_type != "planks" and rep_count > 0:
            overall_feedback.append(f"Completed {rep_count} repetitions")
        elif exercise_type == "planks" and total_plank_time > 0:
            overall_feedback.append(f"Held plank for {total_plank_time:.1f} seconds total")
        
        return ExerciseAnalysisResult(
            exercise_type=exercise_type,
            total_frames=total_frames,
            frames_with_pose=poses_detected,
            analysis_duration=time.time() - start_time,
            total_reps=rep_count if exercise_type != "planks" else None,
            plank_duration=total_plank_time if exercise_type == "planks" else None,
            repetitions=repetitions,
            plank_sessions=plank_sessions,
            average_form_score=avg_form_score,
            overall_feedback=overall_feedback,
            form_feedback=form_feedback,
            best_rep_quality=best_rep_quality,
            consistency_score=1.0 - (np.std([rep.form_quality for rep in repetitions]) if repetitions else 0)
        )
    
    def check_service_health(self) -> Dict[str, Any]:
        """Check if MediaPipe and OpenCV are working"""
        try:
            # Test MediaPipe
            mp_test = mp.solutions.pose.Pose()
            mp_available = True
        except:
            mp_available = False
        
        try:
            # Test OpenCV
            test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
            opencv_available = True
        except:
            opencv_available = False
        
        return {
            "mediapipe_available": mp_available,
            "opencv_available": opencv_available,
            "service_ready": mp_available and opencv_available
        }

# Create singleton instance
vision_service = VisionService()