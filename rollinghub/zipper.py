import zipfile
import io
import os


def extract_zip(input_zip):
    input_zip = zipfile.ZipFile(input_zip)
    return {os.path.basename(name): input_zip.read(name)
            for name in input_zip.namelist()}


def make_zip(folder_name, zip_files):
    file_in_mem = io.BytesIO()
    with zipfile.ZipFile(file_in_mem, "a", zipfile.ZIP_DEFLATED, False) as output_zip:
        for f in zip_files:
            output_zip.writestr('\\'.join([folder_name, f[0]]), f[1])
        for zfile in output_zip.filelist:
            zfile.create_system = 0
    file_in_mem.seek(0)
    return file_in_mem
