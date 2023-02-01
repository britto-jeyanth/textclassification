import logging
import base64
import io
import PyPDF2
import json
import os
import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient


def main(myblob: func.InputStream):
    logging.info(f"--- Python blob trigger function processed blob \n"
                 f"----- Name: {myblob.name}\n"
                 f"----- Blob Size: {myblob.length} bytes")

    
    # Convert file content to bytes
    endpoint = "https://medicalclassification.cognitiveservices.azure.com/"
    key = "578e9544d03b4facbaacf2025fb58be2"

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    blob_bytes = myblob.read()

    # Extract original PDF file name
    pdf_prefix_file_name = ''.join(myblob.name.split('.pdf')[:1])
    pdf_prefix_file_name = pdf_prefix_file_name[14:]
    logging.info(f"File Prefix: {pdf_prefix_file_name}")

    # Establish HOME directory for writing/reading temporary files
    HOME_LOCAL_DIR = os.environ['HOME']
    logging.info(f"HOME_DATA_DIR: {HOME_LOCAL_DIR}")
    
    # Open multi-page PDF file
    with io.BytesIO(blob_bytes) as open_pdf_file:
        read_pdf = PyPDF2.PdfReader(open_pdf_file)

        logging.info(len(read_pdf.pages))

        poller = document_analysis_client.begin_analyze_document(
                "MedicalDocExtractionNeural", document=read_pdf
            )
        result = poller.result()
        
        d = [page.to_dict() for page in result.documents]
        logging.info(f"Result: {d}")

        # Extract each page and write out to individual files
        # pdf_list = []
        # for i in range(len(read_pdf.pages)):
        #     output = PyPDF2.PdfWriter()
        #     output.add_page(read_pdf.pages[i])
            
        #     # Temporarily write PDF to disk
        #     temp_pdf_fn = pdf_prefix_file_name +'_'+ str(i + 1)+ str(".pdf")
        #     temp_pdf_fp = os.path.join(HOME_LOCAL_DIR, temp_pdf_fn)
        #     with open(temp_pdf_fp, "wb") as outputStream:
        #         output.write(outputStream)

        #     connection_string = "DefaultEndpointsProtocol=https;AccountName=test9d40;AccountKey=VmVaBaq9MPu//AyWR/1o+q+BP1fidv4fdyuyHOSYAYybGbMNJIypAhslyd3eVdJL+xO4F+kG+2aR+AStEB6aTg==;EndpointSuffix=core.windows.net"
        #     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        #     blob_client = blob_service_client.get_blob_client(container="pdf-documents-single", blob=temp_pdf_fn)
        #     # Read back in the PDF to get the bytes-like version
        #     with open(temp_pdf_fp, 'rb') as temp_pdf_file:
        #         blob_client.upload_blob(temp_pdf_file)
                # file_data = base64.b64encode(temp_pdf_file.read()).decode()

                # Record the filename and the bytes-like data of single-page PDF
            #     ind_pdf = {
            #         'fileName': temp_pdf_fn,
            #         'fileContent': file_data
            #     }

            # pdf_list.append(ind_pdf)
    
    # Finalize response object
    # respObj = {
    #     'individualPDFs': pdf_list
    # }

    # return func.HttpResponse(body=json.dumps(respObj))
