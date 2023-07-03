import os
import numpy as np

def truncate_npy_files(directory, max_file_size):

    for filename in os.listdir(directory):

        if filename.endswith('.npy'):
            file_path = os.path.join(directory, filename)
            file_size = os.path.getsize(file_path)

            if file_size > max_file_size:

                data = np.load(file_path)
                

                max_elements = int(max_file_size / data.itemsize)//784
                

                data_truncated = data[:max_elements]
                

                np.save(file_path, data_truncated)
                
                print(f"File {filename} truncated and saved.")
            else:
                print(f"File {filename} is already under the size limit.")

if __name__ == '__main__':
     truncate_npy_files('data', 75 * 1024 * 1024)
