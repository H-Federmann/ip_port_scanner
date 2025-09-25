=======================================================================================
                  ╔══════════════════════════════════════════╗                 
                  ║                                          ║                 
                  ║                _   _  ______             ║                 
                  ║               | | | ||  ____|            ║                 
                  ║               | |_| || |__               ║                 
                  ║               |  _  ||  __|              ║                 
                  ║               | | | || |                 ║                 
                  ║               |_| |_||_|                 ║                 
                  ║                                          ║                 
                  ╚══════════════════════════════════════════╝                  
                                      
                                      H.F                                        
=======================================================================================

Project : IP & Port Scanner  
Version : 1.0.0  
Author  : H. Federmann  
Release : 2025-09-25  

=======================================================================================
FEATURES
=======================================================================================
✔ Ping hosts inside a single-octet IP range (e.g. 192.168.1.1 → 192.168.1.254)  
✔ Port-scan per host with customizable port ranges  
✔ Reverse DNS (hostname resolution) for reachable hosts  
✔ Live GUI table output showing open ports only  
✔ Progress bar with centered percentage overlay  
✔ Animated status display of currently scanning IPs  
✔ Export scan results to CSV (semicolon-separated for Excel compat)  
✔ Hotkeys:  
   • Ctrl+X → Start scan  
   • Ctrl+C → Stop scan  
   • Ctrl+S → Export CSV  

=======================================================================================
🧩 COOL STUFF (Retro Edition)
=======================================================================================
A little visual flourish — a tiny retro "network / progress" badge:

   [=----=>]  Scan in progress...  
    .-.       .-.       .-.       .-.  
   ( o )     ( o )     ( o )     ( o )   <- LAN Nodes  
    `-’       `-’       `-’       `-’    
       \       |       /            
        \      |      /             <- Network Links  
         `-.___|__.-'                <- HF Release

![Demo GIF](docs/demo.gif)  

   /\_/\       <- Cat Mascot  
  ( o.o )     
   > ^ <       

Everything in this tool is tuned for quick LAN sweeps and readable, exportable results.  
Think retro release-info aesthetics with modern usability — clean, fast, and useful.

=======================================================================================
STRUCTURE
=======================================================================================
/ip_port_scanner  
 ├─ scanner.py        → Main Application & GUI  
 ├─ README.md         → This file (Retro release-info style & Demo)  
 ├─ README.txt        → Retro text-only version  
 ├─ requirements.txt  → Dependency notes (none required)  
 └─ /examples         → (optional) sample CSV outputs / presets  
 └─ /docs             → Demo GIFs, screenshots  

=======================================================================================
QUICK START
=======================================================================================
1) Ensure your system supports a desktop GUI and basic networking.  

2) Run the scanner script / executable:  
   python scanner.py  

3) In the GUI:  
   - Enter Start IP and End IP (e.g., 192.168.178.1 → 192.168.178.254)  
   - Enter Start Port and End Port (e.g., 20 → 1024)  
   - Click "Start Scan" or press Ctrl+X  
   - Results (OPEN ports + unreachable hosts) appear live in the table  
   - Stop anytime with "Stop Scan" or Ctrl+C  
   - Export with "Export CSV" or Ctrl+S  

=======================================================================================
TIPS & NOTES
=======================================================================================
• Optimized for local networks — scanning large public IP ranges is slow and  
  may be considered abusive. Only scan networks you are authorized to test.  
• Ping uses the system `ping` command for broad compatibility.  
• Port checks use TCP connect() — no raw sockets required (no admin needed).  
• CSV uses semicolon (`;`) for Excel compatibility in some locales.  
• Recommended: run on systems with standard desktop GUI & networking support.  

=======================================================================================
TECHNICAL (neutral)
=======================================================================================
• GUI: native themed widgets (follows system look)  
• Concurrency: threaded scanning (keeps UI responsive)  
• Export: Save dialog with prefilled filename:  
  scan_<startIP>-<endIP>_<startPort>-<endPort>_<timestamp>.csv  
• Behavior:  
  - Only OPEN ports are shown (compact output)  
  - Unreachable hosts listed once with status "Unreachable"  
  - Progressbar reflects total tasks (IPs × ports) as percent  

=======================================================================================
EXTRAS / FUTURE IDEAS
=======================================================================================
• Presets for common port groups & save/load profiles  
• Verbose mode to list closed ports (optional)  
• JSON / XLSX export options  
• Service banner grabs (HTTP header, SSH banner)  
• Scheduled scans & log rotation  

=======================================================================================
LICENSE & DISCLAIMER
=======================================================================================
Use at your own risk. This tool is provided as-is for educational and authorized  
administrative use. Do NOT scan networks without explicit permission.  

=======================================================================================
CREDITS
=======================================================================================
Concept & Code  : H. Federmann  
Design          : Retro Release-Info Style  

=======================================================================================
🚀 H.Federmann’s IP & Port Scanner — Scan Smart & Scan Responsible  
=======================================================================================
