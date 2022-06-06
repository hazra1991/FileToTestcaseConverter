import json
from flatten_dict import flatten
from unflatten_dict import unflatten
from core import CsvParser , XlsxParserGen
from core import Error


plugParser = {

    'csv' : CsvParser,
    'xlsx' : XlsxParserGen,
    'xls' : XlsxParserGen 
}


class FileToTestcaseConverter:
    """ Generates the test file from the given csv
    Support is limited to nested dicts and dicts inside lists are not currently supported
    List can act as values and not as chain dicts
    """

    def __init__(
        self,parser_type : str ='csv',
        schema_file : str=None ,
        input_file : str=None ,
        output_file : str=None ,
        trim_headers : bool=False,
        flatten_key_delimiter : str='dot',
        **kw):

        with open(schema_file,'r') as schema:
            self.schema = json.load(schema)
        self.parser_type = parser_type
        self.flatten_key_delimiter = flatten_key_delimiter
        self.flatten_schema = flatten(self.schema,reducer=flatten_key_delimiter,enumerate_types=(list,))  # Dict flattening is done by '.'
        self.update_schema_file = kw.pop('update_schema_file',None)
        if self.update_schema_file:
            self.updateSchema()
        self.input_file = input_file
        self.output_file = output_file
        self.rec_identifier_col = None   # row index or identifier column name
        self.processed_row_id = set()      # stores the index or identifiers for all the processed rows 
        self.column_names = None
        self.processed_rec_buffer = {}
        self.trim_headers=trim_headers
        self.worksheet_name = kw.get('worksheet_name',None)
        self.kw = kw
        
    
    def process(self):

        data_parser = plugParser[self.parser_type](input_file=self.input_file,trim_headers=self.trim_headers,**self.kw)
        records = data_parser.get_records()
        headers = data_parser.get_headers()
        self.rec_identifier_col = headers[0]
        self.column_names = headers[1:]
        self.perform_basic_checks()
        for row in records:
            self._processrow(row)
        data_parser = None
        with open(self.output_file,"w") as f:
            json.dump(self.processed_rec_buffer,f,indent=2)


    def _processrow(self,row):
        row_id =row[self.rec_identifier_col]
        if not row_id:
            raise Error.InvalidRecord(f'The row index at {len(self.processed_row_id)+1} is invalid or null')
        row_id = row_id.strip()
        if row_id not in self.processed_row_id:
            
            for col in self.column_names:
                row_col_val = row[col]
                if row_col_val is None:
                    row_col_val = ""
                elif isinstance(row_col_val,str):
                    if row_col_val.lstrip('-').isdecimal():
                        row_col_val = int(row_col_val)
                    elif row_col_val.lstrip('-').replace('.','',1).isdigit():
                        row_col_val = float(row_col_val)
                    
                self.flatten_schema[col] = row_col_val
            self.processed_row_id.add(row_id)
            self.processed_rec_buffer[row_id] = unflatten(self.flatten_schema,splitter=self.flatten_key_delimiter)
        else:
            msg = f"Duplicate row id found for the id '{row_id}' at row number '{len(self.processed_row_id)+1}'"
            raise Error.DuplicateRowIdFound(msg)


    def perform_basic_checks(self):
        temp = set()
        for col in self.column_names:
            _t = col
            col = col.strip()
            if col == "" or col is None:
                msg = f"Column name at index {self.column_names.index(_t)+1} missing in input csv,check for blank or whitespaces"
                raise Error.ColumnNotFound(msg)
            if _t not in self.flatten_schema:
                raise Error.PathTranslationError(_t)
            if col in temp:
                msg = f"Column '{col}' is Duplicate in the input file '{self.input_file}'"
                raise Error.DuplicateColumnFound(msg)
            temp.add(col)
        return True
    
    def updateSchema(self):
        with open(self.update_schema_file,'r') as fd:
            update_param = json.load(fd)
            for col in update_param:
                if col in self.flatten_schema:
                    self.flatten_schema[col] = update_param[col]
                else:
                    raise Error.PathTranslationError(col)