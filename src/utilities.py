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


def read_all_levels_in_folder(folder_path):
    levels = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith('.txt') and os.path.isfile(file_path):
            level_matrix = read_level_from_txt(file_path)
            levels.append((level_matrix, file_name))
    return levels


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


def get_level_dimensions(level_matrix):
    return len(level_matrix), max([len(row) for row in level_matrix])


def convert_level_to_numeric(level_matrix):
    numeric_level = []
    for row in level_matrix:
        numeric_row = []
        for cell in row:
            if cell == "@":
                numeric_row.append(1)
            elif cell == "$":
                numeric_row.append(2)
            elif cell == ".":
                numeric_row.append(3)
            elif cell == "#":
                numeric_row.append(4)
            elif cell == " ":
                numeric_row.append(0)
        numeric_level.append(numeric_row)

    return numeric_level


def flatten_level_matrix(level_matrix, m, n):
    flattened_matrix = []
    for row in level_matrix:
        flattened_matrix.extend(row)
        flattened_matrix.extend([" "] * (n - len(row)))
    flattened_matrix.extend([" "] * (m * n - len(flattened_matrix)))

    return flattened_matrix


def flatten_numeric_level_matrix(level_matrix, m, n):
    flattened_matrix = []
    for row in level_matrix:
        flattened_matrix.extend(row)
        flattened_matrix.extend([0] * (n - len(row)))
    flattened_matrix.extend([0] * (m * n - len(flattened_matrix)))

    return flattened_matrix


def convert_levels_to_flattened_numerics_by_dimensions(level_list):
    resulting_dict = {}
    for level, _ in level_list:
        level_dimensions = get_level_dimensions(level)
        if level_dimensions not in resulting_dict:
            resulting_dict[level_dimensions] = []
        flattened_numeric_level = flatten_numeric_level_matrix(convert_level_to_numeric(level), *level_dimensions)
        resulting_dict[level_dimensions].append(flattened_numeric_level)

    return resulting_dict


def check_level_validity(level_matrix, intended_dimensions, check_solvable=True):
    m, n = get_level_dimensions(level_matrix)
    dimension_check = m == intended_dimensions[0] and n == intended_dimensions[1]

    actor_counts = {"@": 0, "$": 0, ".": 0, " ": 0, "#": 0}
    for row in level_matrix:
        for cell in row:
            if cell in actor_counts:
                actor_counts[cell] += 1

    player_count_check = actor_counts["@"] == 1
    crate_storage_location_count_check = actor_counts["$"] == actor_counts["."]

    if check_solvable and player_count_check and crate_storage_location_count_check:
        sokoban_solver = SokobanSolver(level_matrix)
        solvable_check = sokoban_solver.solve()
        solution = None
        if solvable_check:
            solution = sokoban_solver.solution()
    else:
        solvable_check = False
        solution = None

    return dimension_check, player_count_check, crate_storage_location_count_check, solvable_check, solution
