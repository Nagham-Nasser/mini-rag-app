from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
import logging

from .schemes.data import ProcessRequest



logger=logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    data_controller = DataController()
    #validate the file property
    is_valid, result_signal = data_controller.validate_uploded_file(file = file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )
    project_dir_path = ProjectController().get_project_path(project_id = project_id)
    #file_path = os.path.join(project_dir_path, file.filename)
    file_path, file_id = data_controller.generate_unique_file_path(
        original_file_name= file.filename,project_id=project_id)

    try :
        #Write for binary to save the uploaded file on the file path
        async with aiofiles.open(file_path,"wb") as f:
            while chunck := await file.read(app_settings.FILE_DEFAULT_CHUNCK_SIZE):
                await f.write(chunck)
    except Exception as e:
        logger.error(f"Error while uploading the file: {e}") #Put the error in the logs

        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )  
    

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id
            }
    )

#End Point for process the data on the uploaded file
@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str,process_request: ProcessRequest):
    #Get the id,chunck_size,overlap_size from the process request
    file_id = process_request.file_id
    chunck_size = process_request.chunk_size
    overlap_size = process_request.overlap_size


    #intialize object from ProcessController
    process_controller = ProcessController(project_id= project_id)

    #get the content
    file_content = process_controller.get_file_content(file_id= file_id)

    #create the chunks
    file_chunks = process_controller.process_file_content(file_content= file_content, file_id=file_id,
                             chunck_size= chunck_size, overlap_size= overlap_size)
    
    if file_chunks is None or  len(file_chunks) ==0:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "signal": ResponseSignal.PROCESSING_FAILED
            }
        )

    return file_chunks








