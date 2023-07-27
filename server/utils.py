import shutil

def zip_folder(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
