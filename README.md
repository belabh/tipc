### TIPC - Tor IP Changer
---
**Simple python tool to change your IP through Tor**

### Features
- Free and open source
- Change your IP unlimited time through Tor network
- Nice interface
- Easy to use

### Installation
> [!WARNING]
> Currently only Linux is supported. Windows and macOS support is in development.

### Linux
**1**. Install Requirements:
  - **Python**:
    - Ubuntu
      ```bash
      sudo apt install python
      ```
    - Archlinux
      ```bash
      sudo pacman -S python
      ```
    - Fedora
      ```bash
      sudo dnf install python
      ```
  - **Libraries**:
    - Rich → `pip install rich`
    - Requests → `pip install requests`
  - **Tor**:
    - Ubuntu:
      ```bash
      sudo apt install tor
      ```
    - ArchLinux:
      ```bash
      sudo pacman -S tor
      ```
  - **Start Tor service**:
      ```bash
      systemctl enable tor && systemctl start tor
      ```

**2**. Clone the repository:
  ```bash
  git clone https://github.com/belabh/tipc.git
  ```
**3**. Enter the project folder:
  ```bash
  cd tipc
  ```
**4**. Install the tool globally:
  ```bash
  sudo python3 global_install.py
  ```

### Windows:
- **Coming soon.**

### MacOS:
- **Coming soon.**

### Usage

**TIPC** supports 2 different modes:
- **Manual**: Press ENTER to change your IP whenever you want.
- **Auto**: Select times (0 for unlimited) and delay and it will automatically change your IP without any interactions (just keep it running).


To start using your new IP, point your applications to Tor's `SOCKS5` proxy (`127.0.0.1:9050`).

---

#### Browser

**Chrome / Edge (Chromium-based):**
1. Go to `Settings → System → Open your computer's proxy settings`.
2. Set **Manual proxy**:
   - Address: `127.0.0.1`
   - Port: `9050`
3. Save and restart the browser.

**Firefox:**
1. Go to `Settings → General → Network Settings → Settings…`.
2. Select **Manual proxy configuration**.
   - SOCKS Host: `127.0.0.1`
   - Port: `9050`
   - Select **SOCKS v5**
3. Click OK and restart Firefox.

---

#### System-wide

1. Open your **network settings**.
2. Set the **SOCKS5 proxy** to:
   - Address: `127.0.0.1`
   - Port: `9050`
3. Save settings.

Now all system traffic will go through Tor.  
After that, change your IP using **TIPC**.

---

#### Applications / Games

If your application or game supports proxies (by default or via mods), set the proxy to:

- Address: `127.0.0.1`
- Port: `9050`

It will route traffic through Tor and change your IP accordingly.

---

#### Test your new IP

TIPC will show your new IP in the terminal.  
You can also verify in a browser with these websites:

- [https://www.whatismyip.com](https://www.whatismyip.com)
- [https://ipleak.net](https://ipleak.net)
- [https://www.iplocation.net](https://www.iplocation.net)

> [!CAUTION]  
> - Using Tor will **increase your ping/latency**.  
> - **TIPC is not a VPN alternative.** It only changes your IP through Tor and does not fully replace a VPN.  

### Disclaimer
TIPC is intended for **educational and testing purposes only**.  
The author is **not responsible for any misuse or illegal activity** conducted using this tool.  
Always comply with local laws and the terms of service of websites or applications.
