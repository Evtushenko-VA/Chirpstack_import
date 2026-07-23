import sys
import os

import grpc
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))

import device_pb2
import device_pb2_grpc


# =========================
# Настройки
# =========================

SERVER = "server:port"

API_TOKEN = "token"

APPLICATION_ID = "app_id"

DEVICE_PROFILE_ID = "dp_id"

CSV_FILE = "file_name.csv"

# =========================


def get_metadata():
    return (
        ("authorization", f"Bearer {API_TOKEN}"),
    )


def create_device(stub, name, dev_eui):

    request = device_pb2.CreateDeviceRequest(
        device=device_pb2.Device(
            application_id=APPLICATION_ID,
            device_profile_id=DEVICE_PROFILE_ID,
            name=name,
            dev_eui=dev_eui,
        )
    )

    stub.Create(
        request,
        metadata=get_metadata(),
    )


def create_keys(stub, dev_eui, app_key):

    request = device_pb2.CreateDeviceKeysRequest(
        device_keys=device_pb2.DeviceKeys(
            dev_eui=dev_eui,

            # Для LoRaWAN 1.0.x AppKey записывается в nwk_key
            nwk_key=app_key,

            # Можно заполнить и app_key — ChirpStack проигнорирует его
            # для устройств LoRaWAN 1.0.x, но использует для 1.1.
            app_key=app_key,
        )
    )

    stub.CreateKeys(
        request,
        metadata=get_metadata(),
    )


def main():

    df = pd.read_csv(
        CSV_FILE,
        sep=";",
        dtype=str
    ).fillna("")

    channel = grpc.insecure_channel(SERVER)

    device_stub = device_pb2_grpc.DeviceServiceStub(channel)

    total = len(df)

    for i, row in df.iterrows():

        name = row["Name"].strip()
        dev_eui = row["DevEUI"].strip()
        app_key = row["AppKey"].strip()

        print(f"[{i + 1}/{total}] {name}", end=" ")

        try:

            create_device(
                device_stub,
                name,
                dev_eui,
            )

            create_keys(
                device_stub,
                dev_eui,
                app_key,
            )

            print("OK")

        except grpc.RpcError as e:

            print(f"ERROR: {e.code()} - {e.details()}")

        except Exception as e:

            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()