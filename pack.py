import struct
import io
import json
import gzip

def write_string(out, s, s2i, s_occ, token_new, token_1byte, token_2byte):
    if s in s2i:
        idx = s2i[s]
        s_occ[idx] += 1
        if idx <= 255:
            out.write(struct.pack('>BB', token_1byte, idx))
        elif idx <= 65535:
            out.write(struct.pack('>BH', token_2byte, idx))
        else:
            b_str = s.encode('utf-8')
            out.write(struct.pack('>B', token_new))
            out.write(struct.pack('>H', len(b_str)))
            out.write(b_str)
    else:
        idx = len(s2i)
        s2i[s] = idx
        s_occ.append(1)
        b_str = s.encode('utf-8')
        out.write(struct.pack('>B', token_new))
        out.write(struct.pack('>H', len(b_str)))
        out.write(b_str)

def write_value(out, val, s2i, s_occ):
    if val is None:
        out.write(b'\x0c') 
    elif isinstance(val, bool):
        out.write(b'\x11' if val else b'\x12') 
    elif isinstance(val, int):
        if -128 <= val <= 127:
            out.write(struct.pack('>bb', 15, val)) 
        elif -32768 <= val <= 32767:
            out.write(struct.pack('>bh', 14, val)) 
        elif -2147483648 <= val <= 2147483647:
            out.write(struct.pack('>bi', 8, val))  
        else:
            out.write(struct.pack('>bq', 9, val))  
    elif isinstance(val, float):
        out.write(struct.pack('>bf', 7, val))      
    elif isinstance(val, str):
        write_string(out, val, s2i, s_occ, 22, 23, 24) 
    elif isinstance(val, list):
        out.write(b'\x01') 
        for item in val:
            write_value(out, item, s2i, s_occ)
        out.write(b'\x02') 
    elif isinstance(val, dict):
        out.write(b'\x03') 
        for k, v in val.items():
            write_string(out, str(k), s2i, s_occ, 19, 20, 21) 
            write_value(out, v, s2i, s_occ)
        out.write(b'\x04') 
    else:
        raise ValueError(f"Unknown type: {type(val)}")

def pack_city_data(full_data):
    header = full_data['header']
    header['minimap'] = False
    header['preview'] = False
    header['compressed minimap'] = False
    
    header_bytes = json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    header_size = len(header_bytes)

    binary_stream = io.BytesIO()
    string_to_index = {}
    string_occurrences = []
    
    write_value(binary_stream, full_data['data'], string_to_index, string_occurrences)
    binary_data = binary_stream.getvalue()

    gzipped_data = gzip.compress(binary_data, compresslevel=9)

    out = io.BytesIO()
    if header_size >= 65536:
        out.write(struct.pack('>BB I', 0, 0, header_size))
    else:
        out.write(struct.pack('>H', header_size))
        
    out.write(header_bytes)
    out.write(gzipped_data)
    
    return out.getvalue()