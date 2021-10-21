import json


def combine_two_json_files():
    data1 = json.load(open("prepared_log_data_evaluation_1.2.json", "rb"))
    data2 = json.load(open("/mnt/ceph/storage/data-in-progress/data-teaching/"
                           "theses/wstud-thesis-libera/resources/"
                           "prepared_log_data_evaluation_2.json", "rb"))
    for entry in data1:
        data2.append(entry)
    safe_as_json_file(data2, "query_obfuscation_data.json")


def safe_as_json_file(data, filename):
    print("I am saving...")
    json_file = json.dumps(data, indent=3)
    f = open(filename, "w")
    f.write(json_file)
    f.close()


if __name__ == '__main__':
    combine_two_json_files()
