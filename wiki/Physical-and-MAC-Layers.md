# 📡 Physical & MAC Layers (IEEE 802.11p)

This document describes the modeling of the Physical Layer and Medium Access Control (MAC) layer based on the **IEEE 802.11p (WAVE / DSRC)** standard, including mathematical derivations of radio propagation formulas.

---

## 1. IEEE 802.11p DSRC Wireless Standard

The IEEE 802.11p amendment is tailored for communications in vehicular environments characterized by rapid mobility and multipath fading:

- **Frequency Spectrum**: Dedicated Short-Range Communications (DSRC) band operating between $5.850\text{ GHz} - 5.925\text{ GHz}$ ($5.9\text{ GHz}$).
- **Channel Bandwidth**: Narrow **$10\text{ MHz}$** channels (half of standard $20\text{ MHz}$ Wi-Fi) to mitigate Doppler spread and delay spread distortion.
- **Physical Modulation**: Orthogonal Frequency Division Multiplexing (OFDM) utilizing 52 active subcarriers.
- **Medium Access**: Carrier Sense Multiple Access with Collision Avoidance (CSMA/CA) supported by Enhanced Distributed Channel Access (EDCA) QoS prioritization.

---

## 2. INET Radio Configuration

In `vanet_aodv/omnetpp.ini`, the physical layer is instantiated via **`Ieee80211DimensionalRadio`** and **`Ieee80211DimensionalRadioMedium`**:

```ini
##########################################################
#                  Physical Environment                  #
##########################################################
*.physicalEnvironment.config = xmldoc("empty.xml")
*.radioMedium.backgroundNoise.power = -110dBm
*.radioMedium.mediumLimitCache.centerFrequency = 5.9 GHz

##########################################################
#              IEEE 802.11p NIC Configuration            #
##########################################################
*.node[*].wlan[0].opMode = "p"
*.node[*].wlan[0].radio.typename = "Ieee80211DimensionalRadio"
*.node[*].wlan[0].radio.bandName = "5.9 GHz"
*.node[*].wlan[0].radio.channelNumber = 3
*.node[*].wlan[0].radio.bandwidth = 10 MHz
*.node[*].wlan[0].radio.transmitter.power = 10mW

# Physical Antenna Placement on Vehicle Roof
*.node[*].wlan[*].radio.antenna.mobility.typename = "AttachedMobility"
*.node[*].wlan[*].radio.antenna.mobility.mobilityModule = "^.^.^.^.mobility"
*.node[*].wlan[*].radio.antenna.mobility.offsetX = -2.5m
*.node[*].wlan[*].radio.antenna.mobility.offsetZ = 1.5m
```

### Physical Parameters:
- **`backgroundNoise.power = -110dBm`**: Models the thermal noise floor for a $10\text{ MHz}$ channel at ambient temperature $290\text{ K}$.
- **`antenna.mobility.offsetZ = 1.5m`**: Mounts the antenna $1.5\text{ meters}$ above ground (realistic sedan roof level).
- **`antenna.mobility.offsetX = -2.5m`**: Offsets antenna positioning toward vehicle center-roof according to SUMO vehicle dimensions.

---

## 3. Mathematical Derivation of Communication Range

The maximum physical communication range ($d_{max}$) between transmitter ($Tx$) and receiver ($Rx$) is derived using the Friis Free-Space Transmission formula.

### A. Friis Transmission Equation

The received power ($P_{rx}$) at distance $d$ is given by:

$$P_{rx} = P_{tx} \cdot G_{tx} \cdot G_{rx} \cdot \left(\frac{\lambda}{4\pi d}\right)^2$$

Assuming isotropic unity-gain antennas ($G_{tx} = 1, G_{rx} = 1$):

$$P_{rx} = P_{tx} \cdot \left(\frac{\lambda}{4\pi d}\right)^2$$

Where:
- $c = 299,792,458\text{ m/s} \approx 3 \times 10^8\text{ m/s}$ (speed of light)
- $f = 5.9\text{ GHz} = 5.9 \times 10^9\text{ Hz}$
- Wavelength $\lambda$:
  $$\lambda = \frac{c}{f} = \frac{3 \times 10^8\text{ m/s}}{5.9 \times 10^9\text{ Hz}} \approx 0.0508136\text{ m} \approx 5.08\text{ cm}$$

---

### B. Determining Maximum Distance ($d_{max}$)

A frame can be demodulated if the received signal meets or exceeds receiver sensitivity ($P_{rx} \ge P_{rx\_min}$):

$$P_{rx\_min} = P_{tx} \cdot \left(\frac{\lambda}{4\pi d_{max}}\right)^2$$

Dividing both sides by $P_{tx}$:

$$\frac{P_{rx\_min}}{P_{tx}} = \left(\frac{\lambda}{4\pi d_{max}}\right)^2$$

Taking square roots:

$$\sqrt{\frac{P_{rx\_min}}{P_{tx}}} = \frac{\lambda}{4\pi d_{max}}$$

Solving for $d_{max}$:

$$\mathbf{d_{max} = \frac{\lambda}{4\pi} \cdot \sqrt{\frac{P_{tx}}{P_{rx\_min}}} = \frac{c}{4\pi f} \cdot \sqrt{\frac{P_{tx}}{P_{rx\_min}}}}$$

---

### C. Numerical Calculation with Configured Parameters

Using values from `vanet_aodv/omnetpp.ini`:
- Vehicle transmission power: $P_{tx} = 10\text{ mW} = 0.01\text{ W}$ ($+10\text{ dBm}$)
- Sensitivity threshold: $P_{rx\_min} = -85\text{ dBm} = 10^{\frac{-85}{10}}\text{ mW} \approx 3.16228 \times 10^{-12}\text{ W}$

Computing power ratio:
$$\frac{P_{tx}}{P_{rx\_min}} = \frac{10^{-2}\text{ W}}{3.16228 \times 10^{-12}\text{ W}} \approx 3.16228 \times 10^9$$

$$\sqrt{\frac{P_{tx}}{P_{rx\_min}}} \approx 56,234.13$$

Scaling factor:
$$\frac{\lambda}{4\pi} = \frac{0.0508136}{4\pi} \approx 0.0040436\text{ m}$$

Multiplying terms:
$$d_{max} = 0.0040436 \times 56,234.13 \approx \mathbf{226.7\text{ meters}} \approx \mathbf{227\text{ meters}}$$

Thus, under standard 10mW transmission power, the effective physical communication range is **$\approx 227\text{ meters}$**.

---

## 4. Transmission Power vs Range Lookup Table

Based on this derivation at $5.9\text{ GHz}$ with $-85\text{ dBm}$ sensitivity:

| Transmitter Power ($P_{tx}$) | Power in dBm | Theoretical Communication Range ($d_{max}$) | Typical Context |
|:---:|:---:|:---:|---|
| **$2\text{ mW}$** | $+3\text{ dBm}$ | $\approx \mathbf{101\text{ m}}$ | Very dense traffic (mitigates packet collisions) |
| **$5\text{ mW}$** | $+7\text{ dBm}$ | $\approx \mathbf{160\text{ m}}$ | Dense urban grid with short street links |
| **$10\text{ mW}$** *(Default)* | $+10\text{ dBm}$ | $\approx \mathbf{227\text{ m}}$ | **Standard DSRC V2V suburban/urban baseline** |
| **$50\text{ mW}$** | $+17\text{ dBm}$ | $\approx \mathbf{508\text{ m}}$ | Priority vehicles (Emergency, Police, Transit) |
| **$100\text{ mW}$** *(RSU)* | $+20\text{ dBm}$ | $\approx \mathbf{718\text{ m}}$ | **Road-Side Units & Intersection Gateways** |

---

## 5. Significance of `centerFrequency = 5.9 GHz`

In INET Framework, if `centerFrequency` is omitted from `mediumLimitCache`, the radio medium defaults to $2.4\text{ GHz}$ (standard Wi-Fi).
At $2.4\text{ GHz}$, the wavelength is significantly longer ($\lambda \approx 12.5\text{ cm}$), which produces an incorrect, overly large theoretical range of $\approx 560\text{ meters}$.

Explicitly setting:
```ini
*.radioMedium.mediumLimitCache.centerFrequency = 5.9 GHz
```
ensures that path loss models, limit cache cutoffs, and visual circle ranges strictly adhere to physical 5.9 GHz DSRC propagation.
