import random
import time
import urllib.request

URL = "http://127.0.0.1:8181/api/v3/write_lp?db=iot_water_db"

NODES = {
    "node1": {
        "ph": 7.00,
        "temperature": 22.0,
        "turbidity": 0.8,
        "chlorine": 0.60,
        "tds": 320,
        "conductivity": 510,
        "dissolved_oxygen": 8.0,
        "orp": 310,
    },
    "node2": {
        "ph": 7.10,
        "temperature": 22.5,
        "turbidity": 1.0,
        "chlorine": 0.70,
        "tds": 340,
        "conductivity": 525,
        "dissolved_oxygen": 7.9,
        "orp": 315,
    },
    
}

print("🚀 Publishing water quality KPIs for 6 nodes...")

while True:

    lines = []

    print("-" * 90)

    for sensor_id, base in NODES.items():

        ph = round(base["ph"] + random.uniform(-0.15, 0.15), 2)
        temperature = round(base["temperature"] + random.uniform(-0.5, 0.5), 2)
        turbidity = round(max(0, base["turbidity"] + random.uniform(-0.25, 0.25)), 2)
        chlorine = round(max(0, base["chlorine"] + random.uniform(-0.10, 0.10)), 2)
        tds = round(base["tds"] + random.uniform(-15, 15), 1)
        conductivity = round(base["conductivity"] + random.uniform(-20, 20), 1)
        dissolved_oxygen = round(base["dissolved_oxygen"] + random.uniform(-0.3, 0.3), 2)
        orp = round(base["orp"] + random.uniform(-15, 15), 1)

        line = (
            f"water_sensors,sensor_id={sensor_id} "
            f"ph={ph},"
            f"temperature={temperature},"
            f"turbidity={turbidity},"
            f"chlorine={chlorine},"
            f"tds={tds},"
            f"conductivity={conductivity},"
            f"dissolved_oxygen={dissolved_oxygen},"
            f"oxidation_reduction_potential={orp}"
        )

        lines.append(line)

        print(
            f"✅ {sensor_id:5s} | "
            f"pH={ph:.2f} | "
            f"T={temperature:.2f}°C | "
            f"Turb={turbidity:.2f} NTU | "
            f"Cl={chlorine:.2f} mg/L | "
            f"TDS={tds:.1f} ppm | "
            f"Cond={conductivity:.1f} µS/cm | "
            f"DO={dissolved_oxygen:.2f} mg/L | "
            f"ORP={orp:.1f} mV"
        )

    payload = "\n".join(lines)

    try:
        req = urllib.request.Request(
            URL,
            data=payload.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )

        with urllib.request.urlopen(req):
            print("✅ Upload successful.")

    except Exception as e:
        print(f"❌ Upload failed: {e}")

    time.sleep(3)
