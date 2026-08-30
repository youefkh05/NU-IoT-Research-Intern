import spidev
import time


# ============================================================
# Configuration
# ============================================================

SPI_BUS = 0

# 8 sensor nodes
# CE0 ... CE7
NODE_COUNT = 8

SPI_SPEED_HZ = 1_000_000
SPI_MODE = 0

POLL_PERIOD = 0.200       # 200 ms
COMMAND = ord('S')

PACKET_SIZE = 6


# ============================================================
# SPI initialization
# ============================================================

spi = spidev.SpiDev()

spi.open(SPI_BUS, 0)

spi.max_speed_hz = SPI_SPEED_HZ
spi.mode = SPI_MODE
spi.bits_per_word = 8


# ============================================================
# CRC-8
# Polynomial = 0x07
# ============================================================

def crc8(data):

    crc = 0x00

    for byte in data:

        crc ^= byte

        for _ in range(8):

            if crc & 0x80:

                crc = ((crc << 1) ^ 0x07) & 0xFF

            else:

                crc = (crc << 1) & 0xFF

    return crc


# ============================================================
# Read one sensor node
# ============================================================

def read_sensor_node(node):

    # --------------------------------------------------------
    # Select the SPI chip select
    # --------------------------------------------------------

    spi.no_cs = False

    # spidev device selects the hardware CE.
    # For this example we assume node 0 = CE0,
    # node 1 = CE1, etc.
    #
    # Therefore we open the corresponding device here.
    #
    # NOTE:
    # Raspberry Pi hardware normally provides only CE0/CE1.
    # For 8 nodes you need additional GPIO CS lines or
    # a decoder/multiplexer.
    # --------------------------------------------------------

    # This example assumes that CS selection is implemented
    # separately.
    #
    # See the GPIO-CS version below.
    pass


# ============================================================
# Main
# ============================================================

try:

    last_poll = time.monotonic()

    while True:

        now = time.monotonic()

        # ----------------------------------------------------
        # 200 ms polling period
        # ----------------------------------------------------

        if now - last_poll >= POLL_PERIOD:

            # Keep the schedule periodic
            last_poll += POLL_PERIOD

            # ================================================
            # Read all 8 nodes
            # ================================================

            for node in range(NODE_COUNT):

                print(f"Reading node {node}")

                # --------------------------------------------
                # Select node
                # --------------------------------------------

                # CS LOW

                # --------------------------------------------
                # Send 'S'
                # --------------------------------------------

                response = spi.xfer2([COMMAND])

                # --------------------------------------------
                # Generate clocks to receive packet
                # --------------------------------------------

                dummy = [0x00] * PACKET_SIZE

                packet = spi.xfer2(dummy)

                # --------------------------------------------
                # CS HIGH
                # --------------------------------------------

                # --------------------------------------------
                # Validate packet length
                # --------------------------------------------

                if len(packet) != PACKET_SIZE:

                    print(
                        f"Node {node}: invalid packet length"
                    )

                    continue

                # --------------------------------------------
                # Extract data
                # --------------------------------------------

                address = packet[0]

                sensor1 = (
                    (packet[1] << 8)
                    | packet[2]
                )

                sensor2 = (
                    (packet[3] << 8)
                    | packet[4]
                )

                received_crc = packet[5]

                # --------------------------------------------
                # Calculate CRC
                # --------------------------------------------

                calculated_crc = crc8(packet[:5])

                # --------------------------------------------
                # Verify CRC
                # --------------------------------------------

                if calculated_crc != received_crc:

                    print(
                        f"Node {node}: CRC ERROR"
                    )

                    print(
                        f"Received: 0x{received_crc:02X}"
                    )

                    print(
                        f"Expected: 0x{calculated_crc:02X}"
                    )

                    continue

                # --------------------------------------------
                # Verify address
                # --------------------------------------------

                if address != node:

                    print(
                        f"Node {node}: ADDRESS ERROR"
                    )

                    print(
                        f"Received address: {address}"
                    )

                    continue

                # --------------------------------------------
                # Data is valid
                # --------------------------------------------

                print(
                    f"Node {node}: "
                    f"S1={sensor1}, "
                    f"S2={sensor2}"
                )

        # ----------------------------------------------------
        # Other application code can run here
        # ----------------------------------------------------

        # MQTT
        # Database
        # Data processing
        # Network communication
        # etc.


except KeyboardInterrupt:

    print("Stopping...")


finally:

    spi.close()
