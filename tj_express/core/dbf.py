import os
import datetime

def read_dbf(dbf_path: str) -> "pandas.DataFrame":
    """
    Reads a DBF file in a read-only manner and returns a pandas DataFrame.
    Gracefully handles encoding and missing memofiles.
    """
    import pandas as pd
    from dbfread import DBF, FieldParser

    class SafeFieldParser(FieldParser):
        def parseD(self, field, data):
            try:
                return datetime.date(int(data[:4]), int(data[4:6]), int(data[6:8]))
            except ValueError:
                return None

    if not os.path.exists(dbf_path):
        raise FileNotFoundError(f"DBF file not found: {dbf_path}")
    
    with DBF(
        dbf_path, 
        parserclass=SafeFieldParser, 
        load=True, 
        ignore_missing_memofile=True, 
        encoding="cp874", 
        char_decode_errors="ignore"
    ) as table:
        return pd.DataFrame(table)
