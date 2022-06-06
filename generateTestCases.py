import sys
from argparse import ArgumentParser, FileType
from Global import Config
from utils import FileToTestcaseConverter

def get_cli_input():
    worksheet_name = None
    parser = ArgumentParser(description="Test case generator")
    parser.add_argument('-s',"--schema",metavar='',help="flag used to give the template file",default=Config.schema_file)
    parser.add_argument('-us',"--updateschema",metavar='',help="flag used to give the schema update file",default=Config.golbal_schema_update_file)
    parser.add_argument('-in','--inputfile',metavar='<filename/path>',help="Test case files name or path",default=Config.input_file)
    parser.add_argument('-o',"--outputfile",metavar = "<filename/path>",help="The output file nam or path",default=Config.output_file)
    parser.add_argument('--inptype',default=Config.inputfile_type,choices=['csv','xlsx','xls'])
    parser.add_argument('-ls','--listconfig',action="store_true",help="Shows all the configuration set in Global.py")
    exel_ext = ['xlsx' ,'xls']
    if '--inptype' in sys.argv[1:]:
        if any(elem in exel_ext  for elem in sys.argv[1:]):
            if not any(el in ['-ws','--worksheet'] for el in sys.argv[1:]):
                raise ValueError("worksheet flag not provided")
    else:
        if Config.inputfile_type in {'xlsx','xls'}:
            worksheet_name = Config.worksheet_name
    
    parser.add_argument('-ws','--worksheet',metavar="",default=worksheet_name,help='Optional flag to provided the worksheet name for excell formal')
    
    args = parser.parse_args()
    
    if args.inptype.lower() not in {'csv','xlsx','xls'}:
        raise TypeError(f'unsupported file type selected please check the "inputfile_type" = "{args.inptype}"')
    if args.inptype.lower() in {'xlsx','xls'} and (args.worksheet == None or args.worksheet.strip() == ""):
        raise ValueError(f"worksheet not provided for the xlsx file")
    return args


if __name__ == "__main__":
    """ Main Entry point for the program """

    args = get_cli_input()
    
    if args.listconfig:
        print(Config)
        exit()

    gen = FileToTestcaseConverter(
        parser_type=args.inptype.lower(),
        schema_file=args.schema,
        update_schema_file=args.updateschema,
        input_file=args.inputfile,
        output_file=args.outputfile,
        trim_headers=True,
        worksheet_name =args.worksheet
        )
    gen.process()
