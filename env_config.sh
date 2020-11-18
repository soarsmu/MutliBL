# Here we creatre a virtual environment and install necessary libraries
conda create -n multibl python=3.7
source activate multibl
pip install pandas comment_parser python-magic tqdm matplotlib
pip install javalang
pip install xlrd # for dealing with xlsx files
pip install eventlet
pip install timeout-decorator
pip install openpyxl
pip install prettytable
pip install sklearn pyclustering
