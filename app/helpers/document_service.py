from helpers import data_utils


def extract_text(file):

    extracted_text = ""
    file_type = data_utils.detect_file_type(file)

    if file_type == "pdf":
        extracted_text = data_utils.extract_pdf(file)

    elif file_type == "word":
        extracted_text = data_utils.extract_docx(file)

    elif file_type == "csv":
        extracted_text = data_utils.extract_csv(file)

    elif file_type == "excel":
        extracted_text = data_utils.extract_excel(file)
    elif file_type == "powerpoint":
        print("extract pptx")
        extracted_text = data_utils.extract_pptx(file)

    return extracted_text
