import yaml


def read_hypers():
    with open("./src/hyper.yaml", "r") as hyper:
        hyper_dict = yaml.safe_load(hyper)
        return hyper_dict


def get_file_contents(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_file_contents(file_path, contents):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(contents)


def append_file_contents(file_path, contents):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(contents)
