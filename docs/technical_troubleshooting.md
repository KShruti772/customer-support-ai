# Technical Troubleshooting - AstraHome Support

## Connectivity Issues

### Camera Won't Connect to WiFi

**Symptoms**: Camera appears offline in app, fails during setup

**Solutions**:
1. **Check WiFi signal**: Camera requires minimum -50 dBm signal strength
   - Move router closer or use WiFi extender
   - Avoid 5GHz band (cameras support 2.4GHz only)
2. **Restart devices**: Unplug camera for 10 seconds, restart router
3. **Correct password**: Ensure WiFi password is entered correctly (case-sensitive)
4. **Router settings**: Disable MAC filtering temporarily; enable WPA2-PSK

**If still not working**: 
- Reset camera to factory settings (hold reset button 10 seconds)
- Re-run setup flow in the AstraHome app
- Contact support if issue persists

### App Can't Discover Camera

**Symptoms**: App cannot find camera on network during initial setup

**Solutions**:
1. Ensure phone and camera are on the same WiFi network
2. Check that phone's Bluetooth is enabled (required for initial setup)
3. Disable VPN or firewall temporarily
4. Restart the AstraHome app completely (close and reopen)

### Slow Live View

**Symptoms**: Laggy or buffering video stream

**Solutions**:
1. **Check internet upload speed**: Minimum 2 Mbps required for 1080p
2. **Reduce resolution**: Switch from 1080p to 720p in camera settings
3. **Close other bandwidth-using apps**: Streaming, downloads, other cameras
4. **Router QoS**: Enable quality-of-service prioritization for the camera

## Device Setup

### Factory Reset

**Hard reset**: Press and hold the reset button on the camera for 10 seconds
- LED will flash amber rapidly during reset
- Wait 2 minutes for camera to reboot
- Re-run setup in the AstraHome app

### Firmware Updates

**Automatic updates**: Cameras check for updates every 24 hours
- Ensure camera remains connected to WiFi
- Do not disconnect during update (may take 10-15 minutes)
- Manual check: Settings → Firmware Update in the AstraHome app

**If firmware update fails**:
1. Check internet connection
2. Ensure sufficient storage on camera (minimum 100MB free)
3. Try manual update via the AstraHome app
4. Contact support if issue persists

## Audio Issues

### No Sound from Camera

**Symptoms**: Video plays but no audio

**Solutions**:
1. Check microphone mute setting in camera app
2. Verify computer/smartphone audio output is selected
3. Test with a different browser or mobile device
4. Restart the camera and viewing device

### Echo or Feedback

**Symptoms**: Echo during two-way audio communication

**Solutions**:
1. Use headphones instead of device speakers
2. Move camera away from reflective surfaces
3. Reduce speaker volume
4. Enable "Mute microphone when not speaking" in settings

## Power Issues

### Camera Won't Power On

**Symptoms**: No LED indicator, camera unresponsive

**Solutions**:
1. Check power adapter connection
2. Try a different power outlet
3. Use only the included power adapter (5V/2A minimum)
4. Try USB power bank (minimum 5V/2A)

### Intermittent Power Loss

**Symptoms**: Camera randomly goes offline

**Solutions**:
1. Check power cable for damage
2. Try a different power outlet
3. Use a surge protector (not a power strip)
4. If using PoE, verify injector is functioning

## Network Configuration

### Port Requirements

AstraHome cameras require the following ports for outbound connectivity:
- **443 (HTTPS)**: All traffic for cloud connectivity
- **123 (NTP)**: Time synchronization
- **53 (DNS)**: Domain name resolution

These ports must be allowed from the camera to the internet (no inbound port forwarding required).

### Firewall Restrictions

Corporate or guest networks may block required ports:
- Use a personal hotspot as an alternative
- Contact network administrator to whitelist AstraHome domains
- AstraHome domains: *.astrahome.com, *.amazonaws.com (for AWS services)

## Device Specifications

### AstraCam X1
- Power: 5V/1A via USB adapter
- WiFi: 2.4GHz only
- Storage: MicroSD card slot (up to 128GB)
- Video: 1080p at 30fps
- Audio: Built-in microphone, speaker

### AstraCam X2
- Power: 12V/1A barrel jack
- WiFi: 2.4GHz/5GHz dual-band
- Storage: MicroSD card slot (up to 256GB)
- Video: 2K at 30fps HDR
- Audio: Dual microphone, speaker

### AstraPlug P1
- Power: 120V AC (direct plug-in)
- Connectivity: WiFi 2.4GHz
- Power monitoring: 0.5W - 1800W
- Remote control: On/off scheduling

## Helpful Commands

### Ping Camera IP
```
ping 192.168.1.44
```

### traceroute
```
traceroute 192.168.1.44
```

### Check WiFi signal
```
nmcli device wifi signal
```

---

**Still need help?** Visit support.astrahome.com for live chat, or email support@astrahome.com for personalized assistance.