# 🗺️ TheoTown Map Merger (In-Memory Engine)

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![TheoTown](https://img.shields.io/badge/TheoTown-Modding-orange.svg)

A powerful, open-source reverse-engineering web application designed to flawlessly stitch multiple TheoTown city maps into a single, massive super-region.

## ⚠️ The Problem: Why does this tool exist?
As a passionate TheoTown mayor, you've likely encountered this frustration: You build a beautiful, sprawling region across multiple $128 \times 128$ or $256 \times 256$ map tiles. However, the game forces you to load each tile individually. You can't see your entire metropolis alive at once, traffic doesn't simulate seamlessly across borders, and managing a multi-tile city becomes a fragmented experience.

**The Goal:** We wanted to take an existing, actively played region (consisting of 4 separate map files) and **merge them into one giant, unified map** so we can play and expand our megacity comfortably without loading screens.

## ✨ The Solution: Smart Spatial Engine
This tool doesn't just copy and paste files. It deeply decodes TheoTown's proprietary Binary JSON format (`.city`) and restructures the core data:

* **🧠 Smart Spatial Scanning:** Automatically hunts down arrays containing `x` and `y` coordinates across the JSON structure and translates them dynamically. Supports all vanilla buildings, roads, underground pipes, and custom plugin assets!
* **🧩 Grid Stitching:** Accurately calculates and stitches the 1D arrays of the terrain into a perfect massive grid.
* **⚡ In-Memory Processing:** The entire pipeline (Decode $\rightarrow$ Merge $\rightarrow$ Pack) runs entirely in RAM. It never writes temporary files to your hard drive, ensuring a lightning-fast and secure experience.
* **🛡️ Universal Size Support:** Automatically detects your map size ($128, 256, 512$, etc.) and calculates the correct spatial offsets for a $2 \times 2$ region merge.

## 🚀 How to Use (Web App)

You don't need to install Python or understand code to use this tool! 

1. **Locate your Maps:** In TheoTown, go to **Settings $\rightarrow$ Other** and enable **Debug Mode**. Return to your region view to see the specific filenames (e.g., `0_0.city`, `0_8.city`).
2. **Upload:** Open the Web App and upload your 4 `.city` files into their corresponding coordinate slots (Top-Left, Top-Right, Bottom-Left, Bottom-Right).
3. **Merge:** Click the "Merge & Pack" button.
4. **Play:** Download the generated `BIG_MAP.city` file, drop it into your game's `regions` folder, and enjoy your new megacity!

*(Note: This tool specifically supports merging a $2 \times 2$ grid of maps into 1).*

## 🛠️ Running Locally (For Developers)

If you wish to run the Streamlit app on your local machine:

1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)

2. Install the required dependency:
   ```bash
   pip install streamlit

3. Run the application:
   ```bash
   streamlit run app.py

⚖️ Disclaimer & Legal
This tool is an unofficial, fan-made utility for TheoTown. It is not affiliated with, endorsed, or sponsored by Lobby Divinus or blueflower.

This tool was created strictly for educational purposes and to enhance the community modding experience. Always back up your city files before modifying them! The author is not responsible for any corrupted save files.

📜 License
This project is open-sourced under the MIT License. You are free to use, modify, and distribute this software. See the LICENSE file for more details.
