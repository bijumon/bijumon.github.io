## user
after installing a new sata drive, case fans in my lianli 216 does not work, help
## assistant

If your case fans in the Lian Li Lancool 216 stopped working after installing a new SATA drive, here’s a checklist to troubleshoot the issue step-by-step:

---

## 🧾 1. **Check Power Connections**
### 🔌 SATA Power and Shared Lines
- Installing a new SATA drive may have required re-routing or splitting SATA power cables.
- **Make sure fan hub or fans are still properly connected to the PSU.**
    - Many case fans (especially front fans in the Lian Li 216) connect to a **fan hub** powered by SATA.
    - Recheck if the SATA power cable for the fan hub got unplugged, or if it was repurposed for the new drive.

---

## 🧾 2. **Inspect the Fan Hub**
### 🔧 Lian Li 216 Fan Setup
- This case usually uses **a built-in fan hub**.
    - **Front 160mm fans** may be powered and controlled via this hub.
- Ensure the **SATA power cable** is connected securely to the hub.
- Also confirm whether the hub’s **PWM connector** (goes to motherboard fan header like CHA_FAN or SYS_FAN) is still connected.

---

## 🧾 3. **BIOS/UEFI Fan Settings**
- Boot into BIOS and check if your motherboard detects the case fans:
    - Check **"Monitor"** or **"Fan control"** section.
    - If no RPM is detected for chassis fans, they may be unplugged or unpowered.

---

## 🧾 4. **Try Direct Fan Connection**
- Unplug one of the case fans from the hub and plug it **directly into a motherboard fan header** (like CHA_FAN1).
    - If it spins, the fan itself is fine, and the issue is likely the hub or power supply to the hub.

---

## 🧾 5. **Check for Electrical Overdraw or PSU Issues**
- If you added a SATA drive on the same cable powering the fan hub, it’s possible the PSU rail or cable can’t handle the combined load.
    - Try moving the new SATA drive to a **different SATA power cable/rail** from the PSU.

---

## 🧾 6. **Inspect for Shorts or Loose Cables**
- Double-check for:
    - Loose or bent fan pins
    - Any shorts (e.g., exposed wires, contact with metal case)
    - Dust or debris in connectors

---

## 🧪 7. **Test With a Known Good SATA Power Cable**
- Temporarily disconnect the new SATA drive and use its power cable for the fan hub.
    - If the fans start spinning again, your previous SATA power connection is faulty or overloaded.

---

### ✅ Final Suggestion:
If everything looks fine but the hub is dead:
- Try resetting the system (turn off PSU, unplug power cord, press power button 5 seconds, replug).
- If still dead, contact Lian Li for replacement fan hub (if under warranty).

---

If you can share:
- How the fans were connected (direct to motherboard vs. hub)?
- Whether they ever spin briefly during boot?
- Which PSU model you're using?

…I can help pinpoint it better.