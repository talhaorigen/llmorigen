
from typing import List, Tuple
from prepare_vectordb import PrepareVectorDB
from load_config import LoadConfig
from summarizer import Summarizer
APPCFG = LoadConfig()
import os
import shutil

class UploadFile:


    @staticmethod
    def process_uploaded_files(files_dir: List, chatbot: List, rag_with_dropdown: str) -> Tuple:

        if rag_with_dropdown == "Process for RAG":
            # persist_dir = APPCFG.custom_persist_directory
            # if os.path.exists(persist_dir):
            #     shutil.rmtree(persist_dir)
            # os.makedirs(persist_dir, exist_ok=True)
            # persist_dir = "data/vectordb/uploaded/chroma/"
            # if os.path.exists(persist_dir):
            #     shutil.rmtree(persist_dir)

            prepare_vectordb_instance = PrepareVectorDB(data_directory=files_dir,
                                                        persist_directory=APPCFG.custom_persist_directory,
                                                        embedding_model_engine=APPCFG.embedding_model_engine,
                                                        chunk_size=APPCFG.chunk_size,
                                                        chunk_overlap=APPCFG.chunk_overlap)
            
            prepare_vectordb_instance.clear_vectordb()
            prepare_vectordb_instance.prepare_and_save_vectordb()
            chatbot.append(
                (" ", "Uploaded files are ready. Please ask your question"))
        elif rag_with_dropdown == "Give Full Summary":
            final_summary = Summarizer.summarize_the_pdf(file_dir=files_dir[0],
                                                         max_final_token=APPCFG.max_final_token,
                                                         token_threshold=APPCFG.token_threshold,
                                                         gpt_model=APPCFG.llm_engine,
                                                         temperature=APPCFG.temperature,
                                                         summarizer_llm_system_role=APPCFG.summarizer_llm_system_role,
                                                         final_summarizer_llm_system_role=APPCFG.final_summarizer_llm_system_role,
                                                         character_overlap=APPCFG.character_overlap)
            chatbot.append(
                (" ", final_summary))
        else:
            chatbot.append(
                (" ", "If you would like to upload a PDF, please select your desired action in 'rag_with' dropdown."))
        return "", chatbot
