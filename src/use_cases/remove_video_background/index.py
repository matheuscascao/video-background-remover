import base64
import os
import requests
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from typing import List
from PIL import Image
import glob
import numpy as np
import moviepy.editor as mpy
import cv2
import rembg
# import hashlib
import secrets
import shutil
import platform
import uuid
from datetime import datetime, timedelta

from typing import List

from config import settings


class RemoveVideoBackground:
    def __init__(self) -> None:
        execution_id = uuid.uuid4()

        self.unprocessed_frames_folder = f"temp/{execution_id}/frames"
        self.processed_frames_folder = f"temp/{execution_id}/processed"
        self.processed_frames_with_background_folder = f"temp/{execution_id}/processed_with_background"
        self.video_folder = f"temp/{execution_id}/video"
        current_platform = platform.system()

        self._delete_old_folders(current_platform)

    def process_remove_video_background_cpu(self, video_file: UploadFile) -> StreamingResponse:
        video_fps = self._extract_frames_from_video(video_file)
        self._remove_background_from_frames_cpu()
        self._add_background_to_video()
        current_platform = platform.system()

        video_name = video_file.filename
        # video_name = video_name.replace(".", "") #TODO: CASOS EM QUE O ARQUIVO CONTÉM . NO NOME
        file_name_without_format = video_name.split(".")[0]
        file_format = video_name.split(".")[1]
        file_name_output = f"{file_name_without_format}_processed.{file_format}"

        output_video = self._create_video_from_frames(
            fps=video_fps, file_name=file_name_output, current_platform=current_platform)
        return output_video

    def process_remove_video_background_gpu(self, video_file: UploadFile) -> StreamingResponse:
        video_fps = self._extract_frames_from_video(video_file)
        self._remove_background_from_frames_gpu()
        self._add_background_to_video()
        current_platform = platform.system()

        video_name = video_file.filename
        # video_name = video_name.replace(".", "") #TODO: CASOS EM QUE O ARQUIVO CONTÉM . NO NOME
        file_name_without_format = video_name.split(".")[0]
        file_format = video_name.split(".")[1]
        file_name_output = f"{file_name_without_format}_processed.{file_format}"

        output_video = self._create_video_from_frames(
            fps=video_fps, file_name=file_name_output, current_platform=current_platform)
        return output_video

    def _delete_old_folders(self, current_platform):
        folder_to_check = "temp/"
        folders_to_check = glob.glob(os.path.join(folder_to_check, "*"))
        current_time = datetime.now()
        time_difference = timedelta(minutes=10)

        for folder in folders_to_check:

            if os.path.exists(folder):
                creation_time = datetime.fromtimestamp(
                    os.path.getctime(folder))

                time_elapsed = current_time - creation_time

                if time_elapsed > time_difference:
                    if current_platform == 'Windows':
                        try:
                            os.system(f'rmdir /s /q "{folder}"')
                        except Exception as e:
                            print(f"Erro ao excluir a pasta {folder}: {e}")
                    else:
                        os.system(f"rm -rf {folder}")

    def _extract_frames_from_video(self, video: UploadFile) -> int:
        if not video.filename.endswith(('.mp4', '.avi', '.mkv')):
            raise HTTPException(status_code=400, detail="Invalid video format")

        os.makedirs(self.unprocessed_frames_folder, exist_ok=True)

        video_path = os.path.join(
            self.unprocessed_frames_folder, video.filename)
        with open(video_path, 'wb') as f:
            while True:
                chunk = video.file.read(4096)
                if not chunk:
                    break
                f.write(chunk)
                f.flush()

        video_capture = cv2.VideoCapture(video_path)

        fps = video_capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        for frame_index in range(total_frames):
            success, frame = video_capture.read()
            if not success:
                break

            frame_filename = f"frame_{frame_index:04d}.png"
            frame_path = os.path.join(
                self.unprocessed_frames_folder, frame_filename)
            cv2.imwrite(frame_path, frame)

        video_capture.release()
        os.remove(video_path)

        return fps

    def _remove_background_from_frames_gpu(self, model: str = 'u2net') -> List[str]:
        url = f"{settings.STABLE_DIFFUSION_BASE_URL}/rembg"

        os.makedirs(self.processed_frames_folder, exist_ok=True)

        for filename in os.listdir(self.unprocessed_frames_folder):
            image_path = os.path.join(self.unprocessed_frames_folder, filename)
            with open(image_path, "rb") as image_file:
                image = image_file.read()
            image_base64 = base64.b64encode(image).decode("utf-8")
            data = {
                "input_image": image_base64,
                "model": "u2net",
                "return_mask": False,
                "alpha_matting": False,
                "alpha_matting_foreground_threshold": 240,
                "alpha_matting_background_threshold": 10,
                "alpha_matting_erode_size": 10
            }
            response = requests.post(url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                processed_image_bytes = base64.b64decode(
                    response_data["image"])

                # processed_image_path = f'{self.processed_frames_folder}/frame_{frame_index:04d}.png'
                unprocessed_file_index = self._extract_file_index(filename)
                processed_image_path = os.path.join(self.processed_frames_folder,
                                                    f"frame_processed_{unprocessed_file_index}.png")
                with open(processed_image_path, 'wb') as f:
                    f.write(processed_image_bytes)

            else:
                raise HTTPException(
                    status_code=response.status_code, detail="Error processing the image")

    def _remove_background_from_frames_cpu(self) -> List[str]:
        input_folder = self.unprocessed_frames_folder

        os.makedirs(self.processed_frames_folder, exist_ok=True)

        for filename in os.listdir(input_folder):
            image_path = os.path.join(input_folder, filename)

            with open(image_path, "rb") as image_file:
                image = image_file.read()

            processed_image = rembg.remove(image)

            unprocessed_file_index = self._extract_file_index(filename)
            processed_image_path = os.path.join(self.processed_frames_folder,
                                                f"frame_processed_{unprocessed_file_index}.png")

            with open(processed_image_path, 'wb') as f:
                f.write(processed_image)

    def _add_background_to_video(self) -> List[str]:

        os.makedirs(self.processed_frames_with_background_folder,
                    exist_ok=True)

        for filename in os.listdir(self.processed_frames_folder):
            image_path = os.path.join(self.processed_frames_folder, filename)
            with Image.open(image_path) as image:
                processed_image_with_black = Image.new(
                    "RGBA", image.size, (0, 0, 0))
                processed_image_with_black.paste(image, (0, 0), image)

                unprocessed_file_index = self._extract_file_index(filename)
                processed_image_path = os.path.join(self.processed_frames_with_background_folder,
                                                    f"frame_processed_{unprocessed_file_index}.png")

                processed_image_with_black.save(processed_image_path)

    def _create_video_from_frames(self, file_name: str, fps: int, current_platform) -> StreamingResponse:

        os.makedirs(self.video_folder, exist_ok=True)

        frames_path = os.path.join(
            self.processed_frames_with_background_folder, '*.png')
        frame_files = sorted(glob.glob(frames_path))

        first_frame = Image.open(frame_files[0])
        width, height = first_frame.size

        aspect_ratio = width / height

        new_width = int(height * aspect_ratio)

        video_path = os.path.join(self.video_folder, 'video.mp4')
        writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(
            *'mp4v'), fps, (new_width, height))

        for frame_file in frame_files:
            frame = Image.open(frame_file)
            frame_resized = frame.resize((new_width, height))
            frame_resized_bgr = cv2.cvtColor(
                np.array(frame_resized), cv2.COLOR_RGBA2BGR)
            writer.write(frame_resized_bgr)

        writer.release()

        def stream():
            with open(video_path, 'rb') as file:
                while True:
                    data = file.read(4096)
                    if not data:
                        break
                    yield data

        headers = {
            'Content-Disposition': f'attachment; filename={file_name}'
        }

        if current_platform == 'Windows':
            shutil.rmtree(self.unprocessed_frames_folder)
            shutil.rmtree(self.processed_frames_folder)
        else:
            os.system(f'rm -rf "{self.unprocessed_frames_folder}"')
            os.system(f'rm -rf "{self.processed_frames_folder}"')

        return StreamingResponse(stream(), media_type='video/mp4', headers=headers)

    def _extract_file_index(self, filename):
        file_index = filename.split('_')[-1].split(".")[0]
        return file_index