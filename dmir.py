import requests, pandas, sys, webbrowser, json, warnings

# toggle all warnings off
warnings.simplefilter(action='ignore', category=FutureWarning)

# please refer to: refer to: https://confluence.govcloud.dk/pages/viewpage.action?pageId=15303120
# for more information.

def print_help():
    '''
    helper function to display all commands
    '''
    exit('--i               | enter interactive mode\n--default         | execute default request (Årslev (6126) 2018/4/1 to 2018/4/2 with limit 100000)\n--format %type%   | export data as format; csv, json or txt (defaults to csv)\n--show stations   | open browser to display list of all meteorological stations\n--show parameters | open browser to display all available datatypes\n--station %int%   | input the station id to specify from which station to request data\n--type %string%   | input the parameter id to specify the datatype\n--from %Y/m/d%    | input the start date, e.g. 2020/4/2\n--to %Y/m/d%      | input the end date, e.g. 2020/4/4\n--fname %string%  | set the name of the exported file\n--limit %int%     | limit the number of datapoints to a maximum\n--clean %bool%    | true to enable data cleaning, false or ommit to disable (only executed if format is default or csv)\n\nExample:\n\npython dmir.py --station 06126 --type temp_mean_past1h --from 2018/4/1 --to 2018/4/2 --limit 10000 --format csv --fname mydataname')

def print_error(err:str=''):
    '''
    helper function to print errors
    '''
    exit('Command not recognized. Type "--help" to see valid commands.\n%s'%str(err))

def datetime_to_unixtime(dt):
    '''
    method to translate datetime into unit microseconds
    '''
    return str(int(pandas.to_datetime(dt).value*10**-3))

def make_datetime(date:str):
    '''
    convert string input to datetime
    '''
    info = str(date).split('/')
    if len(info) != 3:
        print_error('Input dates are wrongly formatted.')
    return pandas.datetime(int(info[0]),int(info[1]),int(info[2]))

#@DeprecationWarning
def make_header(station:str, datatype:str=None, start_date=None, end_date=None, limit:int=None):
    '''
    construct complete header from arguments
    '''
    header = {'stationId' : station}
    if datatype is not None: header.update({'parameterId' : datatype})
    if start_date is not None: header.update({'from':datetime_to_unixtime(start_date)})
    if end_date is not None: header.update({'to':datetime_to_unixtime(end_date)})
    if limit is not None: header.update({'limit':str(limit)})
    return header

# used in interactive mode
def get_input_station():
    station = input('stationId (int):')
    if station == '':
        # called self if igorned
        return get_input_station()
    return station

# used in interactive mode
def get_input_datatype():
    datatype = input('parameterId (int):')
    if datatype == '':
        # called self if igorned
        return get_input_datatype()
    return datatype

def interactive():
    header = {}
    print('Input arguments:')
    station = get_input_station()
    header.update({'stationId':station})
    datatype = get_input_datatype()
    header.update({'parameterId':datatype})
    
    frm = input('from (Y/m/d):')
    if frm != '':
        header.update({'from':datetime_to_unixtime(make_datetime(frm))})
    else:
        print('Continued without a from-date.')
    to = input('to (Y/m/d):')
    if to != '':
        header.update({'to':datetime_to_unixtime(make_datetime(to))})
    else:
        print('Continued without a to-date.')
    limit = input('limit (int):')
    if limit != '':
        header.update({'limit':limit})
    else:
        print('Continued without a limit.')
    
    print('')
    print('>',header)
    finish = input('Send request (y=yes/n=no)?')
    if finish.lower() == 'y':
        return header
    else:
        return interactive()

def get_argument(arg, args):
    arg = '--' + arg
    for i in range(len(args)):
        if arg == args[i]:
            if arg == '--help':
                print_help()
            elif arg == '--i':
                header = interactive()
                return header
            elif arg == '--default':
                return make_header('06126', 'temp_mean_past1h', make_datetime('2018/4/1'), make_datetime('2018/4/2'), 24)
            else:
                try:
                    return args[i+1]
                except:
                    print_error()
    return None

def clean_data(df:pandas.DataFrame):
    # TODO: create function for data cleaning
    return df

if __name__ == "__main__":

    # load key
    with open('key.txt', 'r') as f:
        __api_key = f.readline()

    args = sys.argv   
    default_name = 'data'
    web = False
    get_argument('help', args)

    show = get_argument('show', args)
    if show is not None:
        if show == 'stations':
            webbrowser.open('https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476619')
        elif show == 'parameters':
            webbrowser.open('https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476616')
        elif show == 'login':
            webbrowser.open('https://sts.govcloud.dk/auth/realms/dmi/protocol/openid-connect/auth?response_type=code&client_id=dmi-apigw&redirect_uri=https://dmiapi.govcloud.dk&scope=openid')
        web = True

    header = get_argument('default', args)
    if header is None:
        header = get_argument('i', args)
        if header is None:
            header = {}

    _format = get_argument('format', args)
    if _format is None:
        _format = 'csv'

    station = get_argument('station', args)
    if station is None and header == {} and web is False:
        print_error()
    header.update({'stationId':station})

    datatype = get_argument('type', args)
    if datatype is not None:
        header.update({'parameterId':datatype})

    frm = get_argument('from', args)
    if frm is not None:
        header.update({'from':datetime_to_unixtime(make_datetime(frm))})

    to = get_argument('to', args)
    if to is not None:
        header.update({'to':datetime_to_unixtime(make_datetime(to))})

    limit = get_argument('limit', args)
    if limit is not None:
        header.update({'limit':limit})
    
    fname = get_argument('fname', args)
    if fname is not None:
        default_name = fname

    header.update({'api-key': __api_key})

    if header != {}:
        r = requests.get(url='https://dmigw.govcloud.dk/metObs/v1/observation', params=header)
        try:
            jsn = r.json() # Extract JSON object
        except:
            print('ERROR | received: %s'%r.content)
            exit('Try other parameters.')
        
        if _format == 'txt':
            with open(default_name + '.txt', 'w') as f:
                f.write(json.dumps(jsn))
        elif _format == 'json':
            with open(default_name + '.json', 'w') as f:
                f.write(json.dumps(jsn, sort_keys=True, indent=4))
        else:
            df = pandas.DataFrame(jsn)
            df['time'] = pandas.to_datetime(df['timeObserved'], unit='us') 
            df = df.drop(['_id', 'timeCreated', 'timeObserved'], axis=1)

            clean = get_argument('clean', args)
            if clean is not None and clean.lower() != 'false':
                df = clean_data(df)
            df.iloc[::-1].to_csv(default_name + '.csv', index=False)
        

