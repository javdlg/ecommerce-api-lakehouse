import os
import glob
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BRONZE_DIR = 'data/bronze'
SILVER_OUTPUT = 'data/silver'

