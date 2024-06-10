import numpy as np
import csv
import matplotlib.pyplot as plt

from src.utilities import *


def get_validity_analysis(generated_levels):
    validity_analysis = {"dimension": [0, 0],
                         "player_count": [0, 0],
                         "crate_storage_location_count": [0, 0]}
                         # "solvable": [0, 0],
                         # "solution": []}
    for level, file_name in generated_levels:
        validity = check_level_validity(level, get_intended_dimensions_from_filename(file_name), check_solvable=False)
        dimension_check, player_count_check, crate_storage_location_count_check, solvable_check, solution = validity
        if dimension_check:
            validity_analysis["dimension"][0] += 1
        validity_analysis["dimension"][1] += 1
        if player_count_check:
            validity_analysis["player_count"][0] += 1
        validity_analysis["player_count"][1] += 1
        if crate_storage_location_count_check:
            validity_analysis["crate_storage_location_count"][0] += 1
        validity_analysis["crate_storage_location_count"][1] += 1
        # if solvable_check:
        #     validity_analysis["solvable"][0] += 1
        # validity_analysis["solvable"][1] += 1
        # if solution is not None:
        #     validity_analysis["solution"].append(len(solution))

    return validity_analysis


def cosine_similarity_between_levels(level1, level2):
    level1 = np.array(level1)
    level2 = np.array(level2)

    cosine_similarity = np.dot(level1, level2) / (np.linalg.norm(level1) * np.linalg.norm(level2))
    return cosine_similarity


def get_novelty_analysis(data_folder, generated_levels, training_set):
    training_set_levels = read_all_levels_in_folder(os.path.join(data_folder, "training_data", training_set))

    generated_levels_by_dimensions = convert_levels_to_flattened_numerics_by_dimensions(generated_levels)
    training_set_by_dimensions = convert_levels_to_flattened_numerics_by_dimensions(training_set_levels)

    novelty_to_training_set = []
    novelty_to_each_other = []
    novelty_to_all = []
    for dimension in generated_levels_by_dimensions:
        for generated_level in generated_levels_by_dimensions[dimension]:
            if dimension not in training_set_by_dimensions:
                novelty_to_training_set.append(1)
                novelty_to_all.append(1)
            else:
                for level in training_set_by_dimensions[dimension]:
                    novelty_value = 1 - abs(cosine_similarity_between_levels(generated_level, level))
                    novelty_to_training_set.append(novelty_value)
                    novelty_to_all.append(novelty_value)
            for level in generated_levels_by_dimensions[dimension]:
                if level != generated_level:
                    novelty_value = 1 - abs(cosine_similarity_between_levels(generated_level, level))
                    novelty_to_each_other.append(novelty_value)
                    novelty_to_all.append(novelty_value)

    novelty_analysis = {"to_training_set": np.average(novelty_to_training_set),
                        "to_each_other": np.average(novelty_to_each_other),
                        "to_all": np.average(novelty_to_all)}

    return novelty_analysis


def analyse_experiment_results(data_folder, training_mode, training_set, n_epochs, temperature, n_generations):
    generated_levels = read_all_levels_in_folder(os.path.join(data_folder, "generated_levels", training_mode))
    validity_analysis = get_validity_analysis(generated_levels)
    novelty_analysis = get_novelty_analysis(data_folder, generated_levels, training_set)

    experiment_analysis = {"training_set": int(training_set.split("-")[2]),
                           "n_epochs": n_epochs,
                           "temperature": temperature,
                           "n_generations": n_generations,
                           "validity": validity_analysis,
                           "novelty": novelty_analysis}

    return experiment_analysis


def analyse_all_experiment_results(data_folder):
    experiment_results = {}

    hypers = read_hypers()
    for training_mode in hypers:
        if "0.5-temp" not in training_mode:
            continue
        experiment_results[training_mode] = analyse_experiment_results(data_folder, training_mode, *hypers[training_mode].values())

    return experiment_results


def store_experiment_results(experiment_results, folder_path):
    csv_columns = [
        "Training Mode", "Training Set Size", "Epochs", "Temperature", "Generations",
        "Validity Dimension", "Validity Player Count", "Validity Crate Storage Location Count",
        "Novelty to Training Set", "Novelty to Each Other", "Novelty to All"
    ]

    csv_data = []
    for key, value in experiment_results.items():
        data = [key]
        data.extend([value["training_set"], value["n_epochs"], value["temperature"], value["n_generations"]])
        data.append(value["validity"]["dimension"][0] / value["validity"]["dimension"][1])
        data.append(value["validity"]["player_count"][0] / value["validity"]["player_count"][1])
        data.append(value["validity"]["crate_storage_location_count"][0] / value["validity"]["crate_storage_location_count"][1])
        data.extend([value["novelty"]["to_training_set"], value["novelty"]["to_each_other"], value["novelty"]["to_all"]])
        csv_data.append(data)

    csv_file = os.path.join(folder_path, "experiment_results.csv")
    with open(csv_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(csv_columns)
        writer.writerows(csv_data)


def visualize_experiment_results(experiment_results, folder_path):
    pass

