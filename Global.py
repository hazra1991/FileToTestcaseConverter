from core import ImmutableConfig

class Config(ImmutableConfig):
    """ Default config class will be used if no other cli flags have been provided """

    schema_file = "SRV_AddAndVerifyFuOrder.json"
    golbal_schema_update_file = "globaldata.json"
    input_file =  "sample.xlsx"
    output_file ="sample_json.json"
    inputfile_type = "xlsx"   # [csv,xlsx,xls] are supported curently 
    worksheet_name = "Sheet2"
    logger_file = "LOG.log"        # TODO 
