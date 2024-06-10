import yaml
import os
from src.sokoban_solver import SokobanSolver


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


def read_level_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [list(row.replace("\n", "").replace("\r", "")) for row in file.readlines()]


def convert_level_to_one_line(level_matrix):
    return "\\n".join(["".join(row) for row in level_matrix])


def get_messages_for_chat_completion(m, n):
    system_info = get_system_info()
    user_info = get_user_info(m, n)
    return [system_info, user_info]


def get_system_info():
    return {"role": "system",
            "content": "You are a Sokoban level generator. "
                       "The level is represented as a grid of characters, with specific symbols representing different elements of the game. "
                       "Here are the symbols used: - `#` represents a wall. - `@` represents the player. "
                       "- `.` represents a storage location. - `$` represents a crate. - ` ` (space) represents an empty space. "
                       "Each level should be a solvable puzzle where all crates can be moved to storage locations. "
                       "The player should start at a reasonable position within the level. "
                       "There should be only one player in a level. The number of crates and storage locations should be equal."}


def get_system_info_text():
    return "{" + (f"\"role\": \"system\", \"content\": \"You are a Sokoban level generator. "
                  f"The level is represented as a grid of characters, with specific symbols representing different elements of the game. "
                  f"Here are the symbols used: - `#` represents a wall. - `@` represents the player. - `.` represents a storage location. "
                  f"- `$` represents a crate. - ` ` (space) represents an empty space. "
                  f"Each level should be a solvable puzzle where all crates can be moved to storage locations. "
                  f"The player should start at a reasonable position within the level. "
                  f"There should be only one player in a level. "
                  f"The number of crates and storage locations should be equal.\"") + "}"


def get_user_info(m, n):
    return {"role": "user", "content": f"Generate a Sokoban level with a size of {m}x{n}."}


def get_user_info_text(m, n):
    return "{" + f"\"role\": \"user\", \"content\": \"Generate a Sokoban level with a size of {m}x{n}.\"" + "}"


def convert_level_matrix_to_jsonl_line(level_matrix):
    m = len(level_matrix)
    n = max([len(row) for row in level_matrix])
    system_info = get_system_info_text()
    user_info = get_user_info_text(m, n)
    one_line = convert_level_to_one_line(level_matrix)
    assistant_info = "{" + f"\"role\": \"assistant\", \"content\": \"{one_line}\"" + "}"
    line = "{" + f"\"messages\": [{system_info}, {user_info}, {assistant_info}]" + "}"

    return line


def create_jsonl_from_folder(folder_path, output_file):
    data = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            level_matrix = read_level_from_txt(os.path.join(folder_path, file))
            data.append(convert_level_matrix_to_jsonl_line(level_matrix))

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(data))


def get_intended_dimensions_from_filename(filename):
    return tuple(filename.split("_")[-1].split(".")[0].split("x"))


def check_level_validity(level_matrix, intended_dimensions):
    dimension_check = (len(level_matrix) == intended_dimensions[0] and
                       max([len(row) for row in level_matrix]) == intended_dimensions[1])

    actor_counts = {"@": 0, "$": 0, ".": 0, " ": 0, "#": 0}
    for row in level_matrix:
        for cell in row:
            if cell in actor_counts:
                actor_counts[cell] += 1

    player_count_check = actor_counts["@"] == 1
    crate_storage_location_count_check = actor_counts["$"] == actor_counts["."]

    if player_count_check and crate_storage_location_count_check:
        sokoban_solver = SokobanSolver(level_matrix)
        solvable_check = sokoban_solver.solve()
        solution = None
        if solvable_check:
            solution = sokoban_solver.solution()
    else:
        solvable_check = False
        solution = None

    return dimension_check, player_count_check, crate_storage_location_count_check, solvable_check, solution
