import os, os.path
import re
from glob import glob
import argparse
from datetime import datetime
import pytz
import calendar
#import string

#works for old files 
#filepatrn = re.compile(r'(?P<strain>[^_\W]+)_(?P<time>\d+)[H|h]rs_(?P<loc>[a-zA-Z]+)\d*_(?P<date>[a-zA-Z]+_\d+|[^_\W]+)?.*stitched.tiff')
#works for new files 
strain_p = r'(?P<strain>[^_\W]+|del_SigB|RFP_only)'
time_p = r'(?P<time>\d+)[H|h]r(s)?'
sectdate_p = r'(?P<date>\d+)_?sect'
location_p   = r'(?P<loc>[a-zA-Z]+)[_]?\d*' # center3 ignore the 3
location_p2   = r'(?P<loc>[a-zA-Z]+)[_]?\d_\d' # center_3_2 ignore the 3 and 2
locationl_p = r'(?P<loc>[a-zA-Z]+|[a-zA-Z]+_[a-zA-Z]+)' # center or center_middle
location_0num_p   = locationl_p  
location_1num_p   = locationl_p + r'\d+' # center?
location_unum_p   = locationl_p + r'_\d+' # center?
date_p = r'(?P<date>[a-zA-Z]+_?\d\d|[^_\W]+|\d+)_sect'
#print(strain_p + '_'+ time_p + '_' + location_p_l + '_' + date_p + '_stitched.tiff')
filepatrn_63x_loc0num_nodate = re.compile(strain_p + '_'+ time_p + '_' + location_0num_p + '_stitched.tiff')
filepatrn_63x_loc1num_nodate = re.compile(strain_p + '_'+ time_p + '_' + location_1num_p + '_stitched.tiff')
filepatrn_63x_locunum_nodate = re.compile(strain_p + '_'+ time_p + '_' + location_unum_p + '_stitched.tiff')
filepatrn_63x_loc0num_date   = re.compile(strain_p + '_'+ time_p + '_' + location_0num_p + '_' + date_p + r'(?:_ns)?' + '_stitched.tiff')
filepatrn_63x_loc1num_date   = re.compile(strain_p + '_'+ time_p + '_' + location_1num_p + '_' + date_p + r'(?:_ns)?' + '_stitched.tiff')
filepatrn_63x_locunum_date   = re.compile(strain_p + '_'+ time_p + '_' + location_unum_p + '_' + date_p + r'(?:_ns)?' + '_stitched.tiff')

filepatrn_10x_classic = re.compile(strain_p + '_'+ time_p +'_' +location_p  + ".tiff")
filepatrn_10x_classic2 = re.compile(strain_p + '_'+ time_p +'_' +location_p2  + ".tiff")
filepatrn_10x_numloc = re.compile(strain_p + '_'+ time_p + r'_\d+_(?P<loc>\d+)_'+ sectdate_p+ ".tiff")
filepatrn_10x_name_numloc = re.compile(strain_p + '_'+ time_p +r'_(?P<loc>[a-zA-Z]+|[a-zA-Z]+_[a-zA-Z]+)_(\d_)?(\d_)?' + sectdate_p+ ".tiff")


dateformats = [ "%b%y" # Feb14
              , "%b_%y" # Feb_14
              , "%B%y" # July15
              , "%B_%y" # July_15
              , "%d%m%y" #080715 
              ]


def get_date_time(string):
    if string is None:
        dflt = "Feb15"
        #print("Failed to parse '{0}' so setting '{1}'".format(datestring, dflt))
        return datetime.strptime(dflt, "%b%y")
    else :
        for dtfmt in dateformats:
            try:
                return datetime.strptime(string, dtfmt) 
            except ValueError:
                pass
                #print("'{0}' wasnt in the format '{1}', trying the next".format(datestring, dtfmt))
        raise ValueError("Failed to parse data '{0}'".format(string))

def get_timestamp(datestring):
    date = get_date_time(datestring)   
    gmt = pytz.timezone('Europe/London')
    date = gmt.localize(date)
    return calendar.timegm(date.timetuple())

# def get_fn_info_63(fn, custom_parse):
    # bn = os.path.basename(fn)
    # #humidity = int(os.path.dirname(fn).split("_")[1].replace("H", ""))
    # #humidity = int(os.path.dirname(fn).split("_")[1].replace("H", ""))
    # strain, time, location, date = filepatrn.match(bn).groups()
    # date = get_timestamp(date)
    # return { "humidity":  20 #humidity
    # , "strain": strain.lower()
    # ,"time": time
    # , "location": location 
    # , "sect_date": date # section date
    # ,"image_date": os.path.getmtime(fn) #image date
    # }

### This was not at all reliable, we manual later.
def file_num_to_location(i, n):
    #print(i, n)
    blocks = 1/(n*2)
    #print(blocks)
    loc = (i/n) - blocks
    if (loc < 1/5) or  (loc > 4/5) :
        return "edge"
    elif (loc > 2/5) and (loc <= 3/5) :
        return "center"
    else:
        return "edgecenter"

def parse_63_filename(fn, custom_parse):
    nodate_ps = [ filepatrn_63x_loc0num_nodate 
                , filepatrn_63x_loc1num_nodate 
                , filepatrn_63x_locunum_nodate ]
    date_ps = [ filepatrn_63x_loc0num_date
              , filepatrn_63x_loc1num_date   
              , filepatrn_63x_locunum_date  ]

    def apply_reg(fn, regex):
        #print("trying: ", regex.pattern)
        bn = os.path.basename(fn)
        res = regex.match(bn).groupdict()#.groups()
        #print(res)
        location = res['loc']
        if ("edge" in location) and \
                (("middle" in location) or ("center" in location)):
            location = "edgecenter"
        results  = { "humidity":  20 #humidity
                   , "strain": res['strain'].lower()
                   , "time": int(res['time'])
                   , "location": location 
                   , "image_date": os.path.getmtime(fn) #image date
                   }
        if "date" in res.keys():
            date = get_timestamp(res["date"])
            results["sect_date"] = date # section date
        else:
            results["sect_date"] = 0 # section date
        return results

    if custom_parse :
        bn = os.path.basename(fn)
        print(custom_parse)
        m = re.compile(custom_parse).match(bn)
        print(m.groupdict())
        return m.groupdict()

    for i, regexp in enumerate(nodate_ps + date_ps):
        #print(regexp)
        try: 
            ret = apply_reg(fn, regexp)
            return ret
        except AttributeError as e:
            #print(e)
            continue
    raise ValueError("Failed to parse filename '{0}'".format(fn))

def parse_10_filename(fn, custom_parse=""):
    def classic(fn):
        bn = os.path.basename(fn)
        m = filepatrn_10x_classic.match(bn)
        location = m.group('loc')
        if ("edge" in location) and \
                (("middle" in location) or ("center" in location)):
            location = "edgecenter"
        return { "strain": m.group('strain').lower()
               , "image_date": os.path.getmtime(fn) #image date
               , "time": int(m.group('time'))
               , "sec_date": 0 # section date
               , "location": location
               }
    
    def classic2(fn):
        bn = os.path.basename(fn)
        m = filepatrn_10x_classic2.match(bn)
        location = m.group('loc')
        if ("edge" in location) and \
                (("middle" in location) or ("center" in location)):
            location = "edgecenter"
        return { "strain": m.group('strain').lower()
               , "image_date": os.path.getmtime(fn) #image date
               , "time": int(m.group('time'))
               , "sec_date": 0 # section date
               , "location": location
               }

    def numloc(fn):
        bn = os.path.basename(fn)
        #dn = os.path.dirname(fn)
        #print("number_loc", fn)
        strain, time, location, sec_date = filepatrn_10x_numloc.match(bn).groups()
        #print(strain, time, location, sec_date)
        #loc = int(location)
        #print(l)
        #splitup = bn.split("_")
        #splitup[3] = "*"
        #reg = "_".join(splitup)
        #n = len(glob(os.path.join(dn, reg))) # number of files like this
        loc = "nowhere" # file_num_to_location(loc, n) # we replace this with human checked

        return { "strain": strain.lower()
               , "time": int(time)
               , "image_date": os.path.getmtime(fn) #image date
               , "location": loc #"{0} of {1} is {2}".format(location, n, loc)
               , "sec_date": get_timestamp(sec_date)
               }
    
    def name_num_loc(fn):
        bn = os.path.basename(fn)
        m = filepatrn_10x_name_numloc.match(bn)
        location = m.group('loc')
        if ("edge" in location) and \
                (("middle" in location) or ("center" in location)):
            location = "edgecenter"
        return { "strain": m.group('strain').lower()
               , "time": int(m.group('time'))
               , "image_date": os.path.getmtime(fn) #image date
               , "location": location
               , "sec_date": get_timestamp(m.group('date'))
               }

    if custom_parse :
        bn = os.path.basename(fn)
        print(custom_parse)
        m = re.compile(custom_parse).match(bn)
        print(m.groupdict())
        return m.groupdict()

    for i, try_func in enumerate([ classic, classic2, numloc, name_num_loc]):
        try: 
            return try_func(fn)
        except AttributeError as e:
            #print(e)
            continue
    raise ValueError("Failed to parse filename '{0}'".format(fn))

def tenx_ignore_files(sfl):
    bad_strings = [ "bead"
                  #, "20x"
                  , '2xqp_24hrs_2_5_2_'
                  , "test_ofrbleach"
                  , "double" 
                  , "1_6-2_230615"
                  , "_1_5_2_240615"
                  , "_2_5_2_"
                  , "_3_5_2_"
                  ]
    filt = sfl.copy()
    for st in bad_strings:
        filt = [f for f in filt if st not in f.lower()] 
    return filt

def get_all_files(pa, end_pat):
    sfl = []
    for f in pa.files: 
        if os.path.isdir(f):
            sfl += glob(os.path.join(f, end_pat))
        else:
            sfl += [f] 
    return sfl


if __name__ == "__main__":
    print ("****************")
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+') 
    parser.add_argument('-d', '--datatype', required=True ) 
    pa = parser.parse_args()

    if pa.datatype == "10x":
        get_fn_info = parse_10_filename
        sfl = get_all_files(pa, "*.tiff" )
        filt = tenx_ignore_files(sfl)
        sfl = filt
    elif pa.datatype == "63x":
        get_fn_info = parse_63_filename
        sfl = get_all_files(pa, "*_stitched.tiff")

    for f in sfl :
        print(f)
        info = get_fn_info(f, None)
        print(info)
        print("\t" + " ".join(map(str, info.values())))

