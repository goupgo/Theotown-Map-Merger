import struct
import json
import gzip
import io

def decode_tiny_int(b):
    val = (b << 1) & 0xFF
    if val >= 128:
        val -= 256
    return val >> 1

def read_unsigned_byte(f):
    b = f.read(1)
    if not b:
        raise EOFError("EOF")
    return b[0]

def parse_value(f, string_cache, token=None, expect_string=False):
    if token is None:
        try:
            b = read_unsigned_byte(f)
        except EOFError:
            return None
    else:
        b = token

    if b == 1:   
        arr = []
        while True:
            next_b = read_unsigned_byte(f)
            if next_b == 2: break 
            arr.append(parse_value(f, string_cache, next_b))
        return arr

    elif b == 3: 
        obj = {}
        while True:
            next_b = read_unsigned_byte(f)
            if next_b == 4: break 
            key = parse_value(f, string_cache, next_b, expect_string=True)
            val = parse_value(f, string_cache)
            obj[str(key)] = val
        return obj

    elif b in (19, 22):
        length = struct.unpack('>H', f.read(2))[0]
        s = f.read(length).decode('utf-8', errors='replace')
        string_cache.append(s)
        return s

    elif b in (20, 23):
        idx = read_unsigned_byte(f)
        if idx < len(string_cache):
            return string_cache[idx]
        return f"__UNKNOWN_STRING_{idx}__"

    elif b in (21, 24):
        idx1 = read_unsigned_byte(f)
        idx2 = read_unsigned_byte(f)
        idx = (idx1 * 256) + idx2
        if idx < len(string_cache):
            return string_cache[idx]
        return f"__UNKNOWN_STRING_{idx}__"

    elif b in (5, 6):
        ub = read_unsigned_byte(f)
        if ub == 0:
            length = struct.unpack('>H', f.read(2))[0]
            s = f.read(length).decode('utf-8', errors='replace')
            string_cache.append(s)
            return s
        else:
            idx = (ub - 1) * 256 + read_unsigned_byte(f)
            if idx < len(string_cache):
                return string_cache[idx]
            return f"__UNKNOWN_STRING_{idx}__"

    elif b == 7:  
        val = struct.unpack('>f', f.read(4))[0]
        return str(val) if expect_string else val
    elif b == 8:  
        val = struct.unpack('>i', f.read(4))[0]
        return str(val) if expect_string else val
    elif b == 9:  
        val = struct.unpack('>q', f.read(8))[0]
        return str(val) if expect_string else val
    elif b == 11: 
        val = read_unsigned_byte(f) > 0
        return "true" if val and expect_string else ("false" if expect_string else val)
    elif b == 12: 
        return None
    elif b == 14: 
        val = struct.unpack('>h', f.read(2))[0]
        return str(val) if expect_string else val
    elif b == 15: 
        val = struct.unpack('>b', f.read(1))[0]
        return str(val) if expect_string else val
    elif b == 16: 
        val = struct.unpack('>d', f.read(8))[0]
        return str(val) if expect_string else val
    elif b == 17: 
        return "true" if expect_string else True
    elif b == 18: 
        return "false" if expect_string else False
    elif b >= 128: 
        val = decode_tiny_int(b)
        return str(val) if expect_string else val
    else:
        return f"__UNKNOWN_BYTE_{b}__"

def extract_theotown_city_stream(f):
    b1, b2 = f.read(2)
    header_size = (b1 << 8) | b2
    if header_size == 0:
        b3, b4, b5, b6 = f.read(4)
        header_size = (b3 << 24) | (b4 << 16) | (b5 << 8) | b6
        
    header_bytes = f.read(header_size)
    header = json.loads(header_bytes.decode('utf-8'))
    
    if not header.get('compressed minimap', False) and header.get('minimap', False):
        f.seek(header['width'] * header['height'] * 4, 1)
        
    try:
        unzipped_data = gzip.decompress(f.read())
        stream = io.BytesIO(unzipped_data)
    except Exception as e:
        return None
    
    if header.get('compressed minimap', False) and header.get('minimap', False):
        stream.seek(header['width'] * header['height'] * 4, 1)
        
    if header.get('preview', False):
        peek_byte = stream.read(1)[0]
        stream.seek(-1, 1) 
        
        if peek_byte != 3: 
            pw = struct.unpack('>i', stream.read(4))[0]
            ph = struct.unpack('>i', stream.read(4))[0]
            stream.seek(pw * ph * 4, 1)
        
    string_cache = []
    try:
        city_data = parse_value(stream, string_cache)
    except Exception as e:
        return None
        
    return {
        "header": header,
        "data": city_data
    }