from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum


class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id= project_id)


    def get_file_extention(self, file_id: str):
        return os.path.splitext(file_id)[-1]
    

    def get_file_loader(self, file_id: str):
        #get the extension
        file_ext = self.get_file_extention(file_id= file_id)

        #combin to get the file path
        file_path = os.path.join(self.project_path , file_id)

        #check the extension to read the file
        if (file_ext == ProcessingEnum.TXT.value ):
            return TextLoader(file_path,encoding = "utf-8")
        if (file_ext == ProcessingEnum.PDF.value):
            return PyMuPDFLoader(file_path)
        return None
    
    def get_file_content(self, file_id: str):
        #get the suitable loader to read the different types of the files
        loader = self.get_file_loader(file_id= file_id)

        #load the data 
        return loader.load() #list of the content of the file



    def process_file_content(self, file_content: list, file_id:str,
                             chunck_size:int = 100, overlap_size: int = 20):
        
        # object from the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size= chunck_size,  # Corrected argument name
            chunk_overlap= overlap_size,  # Corrected argument name
            length_function= len
        )


        # extract the text from the content
        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        #extract the metadata from the content 
        file_content_metadata = [rec.metadata for rec in file_content]

        # create the chuncks
        chuncks = text_splitter.create_documents(
            file_content_texts,
            metadatas = file_content_metadata
        )

        return chuncks






