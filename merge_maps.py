def generate_layout(tile_size):
    step = tile_size // 64
    return {
        f"0_0.json": (0, 0),
        f"{step}_0.json": (tile_size, 0),
        f"0_{step}.json": (0, tile_size),
        f"{step}_{step}.json": (tile_size, tile_size)
    }

def get_value_by_path(data_dict, path):
    d = data_dict.get("data", {})
    try:
        for k in path: d = d[k]
        return d
    except (KeyError, TypeError):
        return None

def merge_1d_grid(maps_dict, path, sample_item, tile_size):
    layout = generate_layout(tile_size)
    grids = {}
    expected_len = tile_size * tile_size
    
    for fname in layout.keys():
        arr = get_value_by_path(maps_dict[fname], path)
        if isinstance(arr, list) and len(arr) == expected_len:
            grids[fname] = arr
        else:
            if isinstance(sample_item, dict):
                grids[fname] = [sample_item.copy() for _ in range(expected_len)]
            else:
                grids[fname] = [0 for _ in range(expected_len)]
                
    merged = []
    keys = list(layout.keys())
    
    for row in range(tile_size):
        merged.extend(grids[keys[0]][row * tile_size : (row + 1) * tile_size])
        merged.extend(grids[keys[1]][row * tile_size : (row + 1) * tile_size])
    for row in range(tile_size):
        merged.extend(grids[keys[2]][row * tile_size : (row + 1) * tile_size])
        merged.extend(grids[keys[3]][row * tile_size : (row + 1) * tile_size])
        
    return merged

def merge_spatial_array(maps_dict, path, tile_size):
    layout = generate_layout(tile_size)
    merged = []
    for fname, (offset_x, offset_y) in layout.items():
        arr = get_value_by_path(maps_dict[fname], path)
        if isinstance(arr, list):
            for item in arr:
                if isinstance(item, dict):
                    new_item = item.copy()
                    if 'x' in new_item: new_item['x'] += offset_x
                    if 'y' in new_item: new_item['y'] += offset_y
                    merged.append(new_item)
    return merged