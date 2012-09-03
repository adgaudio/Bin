"""Prepare given dirty json file for mongoimport by doing these things:
    - Convert ObjectId to $oid
    - Convert datetime to integer values
    - Change single quotes to double quotes where appropriate
"""
import re 
from datetime import datetime

def date2int(match, time_format='"%a, %b %d %Y, %I:%M %p %Z"', grp_idx=0):
    """Given a time string in the first group of an SLE match object,
    return integer string representing that time"""
    time = match.groups()[grp_idx]
    as_int = lambda x: str(datetime.strptime(x, time_format).toordinal())
    return match.group().replace(time, as_int(time))


if __name__ == '__main__':
    f = open('./data/input.json').read()
    # Convert 'new Date' to $date
    f2 = re.sub(r'new Date\(["\'](.*?)["\']\)', r'{ "$date" : "\1" }', f)
    f2 = re.sub('{ *"\$date" *: *([\'"].*?[\'"]) *}', date2int, f2)
    # Convert ObjectId to $oid
    f2 = re.sub(r'(?:new |)ObjectId\([\'"](.*?)[\'"]\)', 
                r'{ "$oid" : "\1" }', f2)
    # Convert single quotes to double quotes when beside a {, (, }, or )
    f2 = re.sub(r'([\:\{\(] ?)\'', r'\1"', f2)
    f2 = re.sub(r'\'( ?[\}\)])', r'"\1', f2)
    open('./data/input2.json', 'w').write(f2)

