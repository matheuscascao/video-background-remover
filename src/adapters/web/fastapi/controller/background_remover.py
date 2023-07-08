from fastapi import APIRouter, status, UploadFile
from fastapi.responses import FileResponse
import shutil

from src.use_cases.remove_video_background.index import RemoveVideoBackground

background_remover = APIRouter()


@background_remover.post('/remove_video_background',
                         status_code=status.HTTP_201_CREATED,
                         description='Removes background from video',
                         response_class=FileResponse)
async def remove_video_background(file: UploadFile):
    execute = RemoveVideoBackground()
    file_output = execute.process_remove_video_background_cpu(file)
    # shutil.rmtree("temp")
    return file_output


@background_remover.post('/remove_video_background_with_gpu',
                         status_code=status.HTTP_201_CREATED,
                         description='Removes background from video',
                         response_class=FileResponse)
async def remove_video_background_with_gpu(file: UploadFile):
    execute = RemoveVideoBackground()
    file_output = execute.process_remove_video_background_gpu(file)
    # shutil.rmtree("temp")
    return file_output

# @background_remover.post('/first_frame', status_code=status.HTTP_201_CREATED, description='Returns the first frame of the video')
# def first_frame_of_video():
#     return {'message': 'Background removed successfully'}
