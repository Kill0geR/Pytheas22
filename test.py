import requests

mac = "64-b5-c6-b0-43-6f"

data = requests.get(f"https://maclookup.app/search/result?mac=64-b5-c6-b0-43-6f")
split_data = data.text.split()

if 'content="Vendor/Company:' in split_data:
    first_idx = all_lst.index('content="Vendor/Company:')
    second_idx = all_lst.index('MAC')
    mac_name = " ".join(all_lst[first_idx + 1:second_idx]).strip(",")
    print(mac_name)
