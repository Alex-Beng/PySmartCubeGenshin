
def devices_selection(devices):
    selected_device = None
    if len(devices) == 0:
        print("No CUBE found")
        assert(selected_device is not None)
    elif len(devices) == 1:
        print(f"Found CUBE: {devices[0].name}")
        selected_device = devices[0]
    else:
        device_names = [d.name for d in devices]
        print("Multiple CUBEs found, please select one: [index]")
        for i, name in enumerate(device_names):
            print(f"{i}: {name}")
        while selected_device is None:
            try:
                selection = int(input("Selection: "))
                selected_device = devices[selection]
            except ValueError:
                print("Invalid selection")
            except IndexError:
                print("Invalid selection")
    return selected_device


def twos_comp(val, bits):
    # convert 2's complement binary string to int
    val = int(val, 2)
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val
