#!/usr/bin/env python3
"""Pin a badge image (and a metadata JSON) to IPFS via Pinata.

Dependency-free (stdlib only). Set PINATA_JWT in the environment.

Usage:
    PINATA_JWT=... python scripts/pin_ipfs.py IMAGE "Event Name" "Description"

Prints the `ipfs://<cid>` of the image - use it as `image_ipfs` when creating
the event (and as VITE_CONTRACT_ID's badge art).
"""
import json
import os
import sys
import urllib.request
import uuid

PIN_FILE = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PIN_JSON = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


def token() -> str:
    t = os.environ.get("PINATA_JWT")
    if not t:
        sys.exit("PINATA_JWT not set (create a JWT at https://app.pinata.cloud)")
    return t


def pin_file(path: str, jwt: str) -> str:
    boundary = "----poap" + uuid.uuid4().hex
    with open(path, "rb") as f:
        content = f.read()
    name = os.path.basename(path)
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'.encode(),
            b"Content-Type: application/octet-stream\r\n\r\n",
            content,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
    )
    req = urllib.request.Request(
        PIN_FILE,
        data=body,
        headers={
            "Authorization": f"Bearer {jwt}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["IpfsHash"]


def pin_json(obj: dict, jwt: str) -> str:
    data = json.dumps({"pinataContent": obj}).encode()
    req = urllib.request.Request(
        PIN_JSON,
        data=data,
        headers={"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["IpfsHash"]


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit("usage: pin_ipfs.py IMAGE 'Name' 'Description'")
    image, name, description = sys.argv[1], sys.argv[2], sys.argv[3]
    jwt = token()

    image_cid = pin_file(image, jwt)
    meta_cid = pin_json(
        {"name": name, "description": description, "image": f"ipfs://{image_cid}"},
        jwt,
    )

    print(f"image_ipfs : ipfs://{image_cid}")
    print(f"metadata   : ipfs://{meta_cid}")


if __name__ == "__main__":
    main()
