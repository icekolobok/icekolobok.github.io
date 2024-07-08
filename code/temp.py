import os
import json


def main():
    path = "in/cc/tt"
    info_list = sorted(os.listdir(f"{path}/info/"))
    out_path = f"{path}/results/"
    for info_file in info_list:
        info = json.load(open(os.path.join(f"{path}/info/", info_file)))
        in_name = os.path.join(out_path, f"{info['id']}.json")
        ot_name = os.path.join(out_path, f"{info['startsAt']} {info['fullName']}.json".replace(':', ';').replace('*', '#').replace('|', '+'))
        if os.path.exists(os.path.join(in_name)):
            os.rename(in_name, ot_name)
        else:
            print(f'no such file: {in_name}')


if __name__ == '__main__':
    main()