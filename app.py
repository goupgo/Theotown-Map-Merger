import streamlit as st
import json
import io
import decode
import merge_maps
import pack

st.set_page_config(page_title="TheoTown Map Merger", page_icon="🗺️", layout="centered")

st.markdown("""
    <style>
    .stApp { max-width: 900px; margin: 0 auto; }
    .css-1d391kg { padding-top: 2rem; }
    h1 { color: #1E3A8A; font-weight: 800; text-align: center;}
    .st-emotion-cache-1v0mbdj > img { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("🗺️ TheoTown Map Merger")
st.markdown("<p style='text-align: center; color: #666;'>Upload raw .city files. The engine will decode, merge, and pack them automatically.</p>", unsafe_allow_html=True)

with st.expander("📖 Instructions"):
    st.write("""
    1. **Identify your map files:** Go to game **Settings -> Other**, then enable **Debug Mode**. Return to your region view to see the specific filename for each map tile.
    2. **Supported Sizes:** This tool supports multiple map sizes (e.g., 128x128, 256x256, 512x512, etc.), but is exclusively designed for **2x2 region configurations** (merging exactly 4 tiles into 1).
    3. **Upload raw files:** Simply upload your raw `.city` files below. No manual decoding is required!
    4. **Ensure correct positioning:** Upload the files into the slots matching their in-game positions (Top-Left, Top-Right, Bottom-Left, Bottom-Right).
    5. **Process:** Click **Merge & Pack Maps**. The system processes everything in-memory to keep your workspace clean.
    """)
    
st.divider()

st.subheader("📤 Upload Raw .CITY Files")
col1, col2 = st.columns(2)

with col1:
    file_tl = st.file_uploader("Top-Left Map (0_0.city)", type=["city", "json"], key="tl")
    file_bl = st.file_uploader("Bottom-Left Map (0_n.city)", type=["city", "json"], key="bl")

with col2:
    file_tr = st.file_uploader("Top-Right Map (n_0.city)", type=["city", "json"], key="tr")
    file_br = st.file_uploader("Bottom-Right Map (n_n.city)", type=["city", "json"], key="br")

st.divider()

if st.button("🚀 FULL PIPELINE: MERGE & PACK", use_container_width=True, type="primary"):
    if not (file_tl and file_tr and file_bl and file_br):
        st.error("⚠️ You must upload all 4 map files to proceed!")
    else:
        try:
            with st.spinner('🔓 Decoding .city files directly in memory...'):
                stream_tl = io.BytesIO(file_tl.getvalue())
                stream_tr = io.BytesIO(file_tr.getvalue())
                stream_bl = io.BytesIO(file_bl.getvalue())
                stream_br = io.BytesIO(file_br.getvalue())

                map_tl = decode.extract_theotown_city_stream(stream_tl)
                map_tr = decode.extract_theotown_city_stream(stream_tr)
                map_bl = decode.extract_theotown_city_stream(stream_bl)
                map_br = decode.extract_theotown_city_stream(stream_br)

                if not all([map_tl, map_tr, map_bl, map_br]):
                    st.error("❌ Failed to decode one or more files. Ensure they are valid .city files.")
                    st.stop()

            with st.spinner('🧩 Stitching grid cells & translating spatial objects...'):
                tile_size = map_tl["header"]["width"]
                target_size = tile_size * 2
                step = tile_size // 64

                k_tl = f"0_0.json"
                k_tr = f"{step}_0.json"
                k_bl = f"0_{step}.json"
                k_br = f"{step}_{step}.json"

                maps = {
                    k_tl: map_tl,
                    k_tr: map_tr,
                    k_bl: map_bl,
                    k_br: map_br
                }

                big_map = maps[k_tl].copy()
                
                big_map["header"]["width"] = target_size
                big_map["header"]["height"] = target_size
                big_map["data"]["width"] = target_size
                big_map["data"]["height"] = target_size
                big_map["data"]["general"]["width"] = target_size
                big_map["data"]["general"]["height"] = target_size
                big_map["header"]["trading"] = []

                array_types = {} 
                def scan_dict(d, current_path):
                    for k, v in d.items():
                        path = tuple(current_path + [k])
                        if isinstance(v, dict):
                            scan_dict(v, list(path))
                        elif isinstance(v, list):
                            if len(v) == tile_size * tile_size:
                                array_types[path] = ("grid", v[0] if v else 0)
                            elif len(v) > 0 and isinstance(v[0], dict) and 'x' in v[0]:
                                array_types[path] = ("spatial", None)

                for m in maps.values():
                    scan_dict(m.get("data", {}), [])

                for path, (arr_type, sample) in array_types.items():
                    target = big_map["data"]
                    for p in path[:-1]:
                        if p not in target: target[p] = {}
                        target = target[p]
                        
                    if arr_type == "grid":
                        target[path[-1]] = merge_maps.merge_1d_grid(maps, path, sample, tile_size)
                    elif arr_type == "spatial":
                        target[path[-1]] = merge_maps.merge_spatial_array(maps, path, tile_size)

            with st.spinner('📦 Encoding Binary JSON & packing to .city format...'):
                final_city_bytes = pack.pack_city_data(big_map)

            st.success("🎉 Complete! Memory cleared. Your Super Map is ready.")
            
            st.download_button(
                label=f"⬇️ DOWNLOAD BIG_MAP_{target_size}.CITY",
                data=final_city_bytes,
                file_name=f"BIG_MAP_{target_size}.city",
                mime="application/octet-stream"
            )
            
            st.balloons()

        except Exception as e:
            st.error(f"❌ An error occurred during the pipeline: {e}")