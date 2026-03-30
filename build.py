import os
import shutil
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Build Custom Meshtastic Firmware overlay")
    parser.add_argument("--branch", default="master", help="Firmware branch or tag to build against")
    parser.add_argument("--device", required=True, help="Meshtastic device target environment (e.g. tbeam, heltec-v3)")
    parser.add_argument("--channel", default="0", help="Custom DM Relay Channel")
    parser.add_argument("--hop-limit", default="2", help="Hop limit for relayed DMs")
    args = parser.parse_args()

    firmware_dir = "firmware"
    modules_dir = os.path.join(firmware_dir, "src", "modules")

    # 1. Clone or update repository
    if not os.path.exists(firmware_dir):
        print(f"Cloning Meshtastic firmware...")
        subprocess.run(["git", "clone", "https://github.com/meshtastic/firmware.git"], check=True)

    # 2. Checkout specified branch/tag
    print(f"Checking out {args.branch}...")
    subprocess.run(["git", "fetch", "--all", "--tags"], cwd=firmware_dir, check=True)
    subprocess.run(["git", "checkout", "-f", args.branch], cwd=firmware_dir, check=True)

    # 3. Copy custom files into firmware folder
    print(f"Overlaying custom files...")
    custom_files = ["DMRelayModule.cpp", "DMRelayModule.h"]
    for file in custom_files:
        src = os.path.join("custom_modules", file)
        dst = os.path.join(modules_dir, file)
        shutil.copy2(src, dst)

    # 4. Patch Modules.cpp
    print(f"Patching Modules.cpp to register DMRelayModule...")
    modules_cpp_path = os.path.join(modules_dir, "Modules.cpp")
    with open(modules_cpp_path, 'r') as f:
        content = f.read()

    if 'DMRelayModule.h' not in content:
        content = content.replace(
            '#include "modules/StoreForwardModule.h"',
            '#include "modules/StoreForwardModule.h"\n#include "DMRelayModule.h"'
        )
        content = content.replace(
            'storeForwardModule = new StoreForwardModule();',
            'storeForwardModule = new StoreForwardModule();\n    dmRelayModule = new DMRelayModule();'
        )
        with open(modules_cpp_path, 'w') as f:
            f.write(content)

    # 5. Build with PlatformIO, passing in build flags
    print(f"Building firmware...")
    env_vars = os.environ.copy()
    
    # Inject our compiler directives
    build_flags = env_vars.get("PLATFORMIO_BUILD_FLAGS", "")
    env_vars["PLATFORMIO_BUILD_FLAGS"] = f"{build_flags} -D DM_RELAY_CHANNEL={args.channel} -D DM_RELAY_HOP_LIMIT={args.hop_limit}".strip()

    print(f"Using PLATFORMIO_BUILD_FLAGS: {env_vars['PLATFORMIO_BUILD_FLAGS']}")
    
    print(f"Building firmware for {args.device}...")
    subprocess.run(["pio", "run", "-e", args.device], cwd=firmware_dir, env=env_vars, check=True)

if __name__ == "__main__":
    main()
