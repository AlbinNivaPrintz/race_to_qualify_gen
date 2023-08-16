import sys
import csv
import argparse
import random
import operator


def load_csv(filename, headers=None):
    with open(filename) as rider_file:
        rider_reader = csv.DictReader(rider_file)
        riders = []
        for row in rider_reader:
            if headers is not None:
                values = []
                for header in headers:
                    value = row[header]
                    value = value.strip().title()
                    values.append(value)
                riders.append(" ".join(values))
            else:
                riders.append(row)

        return riders


def partition(lst, size):
    out = []
    for i in range(0, len(lst), size):
        out.append(lst[i : i + size])
    return out


def shuffled_partition(values, size):
    random.shuffle(values)
    return partition(values, size)


def store_heats_in_set(heats: list[list[str]], s: set):
    for heat in heats:
        heat.sort()
        s.add(tuple(heat))
    return s


def find_next_heat(riders, s, args):
    partition = None
    while True:
        partition = shuffled_partition(riders, args.heat_size)
        has_repeat = False
        for heat in partition:
            heat.sort()
            if tuple(heat) in s:
                has_repeat = True
                break
        if not has_repeat:
            break
    return partition


def store_csv(output_filename, data, headers=None):
    with open(output_filename, "w") as output_file:
        if headers is None:
            headers = list(data[0].keys())
        writer = csv.DictWriter(output_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows([] + data)


def handle_heats(args):
    riders = load_csv(args.input, args.headers)
    out_rows = []
    s = set()
    for round in range(args.rounds):
        partition = find_next_heat(riders, s, args)
        s = store_heats_in_set(partition, s)
        for heat in range(0, len(partition)):
            for competitior in partition[heat]:
                out_rows.append(
                    {
                        "Round": round + 1,
                        "Heat": heat + 1,
                        "Competitor": competitior,
                        "Result": 0,
                    }
                )
    store_csv(args.output, out_rows)


def count_points(results):
    aggregated_results = {}
    beat_opponents = {}
    i = 0
    current_round = results[0]["Round"]
    current_heat = results[0]["Heat"]
    losers = []
    heat_winner = None
    while i < len(results):
        row = results[i]

        if row["Round"] != current_round or row["Heat"] != current_heat:
            if heat_winner is None:
                print("yo")
            beat_opponents.setdefault(heat_winner, []).extend(losers)
            losers = []
            current_round = row["Round"]
            current_heat = row["Heat"]
            heat_winner = None

        aggregated_results.setdefault(row["Competitor"], {"points": 0})

        if int(row["Result"]) == 1:
            heat_winner = row["Competitor"]
        else:
            losers.append(row["Competitor"])

        aggregated_results[row["Competitor"]]["points"] = aggregated_results[
            row["Competitor"]
        ]["points"] + int(int(row["Result"]) == 1)

        i += 1

    # Add Sonneborn-Berger score
    for participant, participant_opponents in beat_opponents.items():
        for opponent in participant_opponents:
            aggregated_results[participant]["sonneborn_berger"] = (
                aggregated_results[participant].get("sonneborn_berger", 0)
                + aggregated_results[opponent]["points"]
            )

    output_list = []

    # Add Buchholz cut 1
    for participant, data in aggregated_results.items():
        data["competitor"] = participant
        data.setdefault("sonneborn_berger", 0)
        output_list.append(data)

    output_list.sort(
        key=operator.itemgetter("points", "sonneborn_berger"), reverse=True
    )

    # Add rank
    for rank in range(0, len(output_list)):
        output_list[rank]["rank"] = rank + 1

    return output_list


def handle_results(args):
    results = load_csv(args.input)
    output_results = count_points(results)
    store_csv(
        args.output,
        output_results,
        headers=("rank", "competitor", "points", "sonneborn_berger"),
    )


def parse_args(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Generate heats
    parser_generate_heats = subparsers.add_parser("heats")
    parser_generate_heats.add_argument(
        "--input", help="input csv riders list", default="riders.csv"
    )
    parser_generate_heats.add_argument(
        "--output", help="output csv rounds", default="rounds.csv"
    )
    parser_generate_heats.add_argument(
        "--headers",
        help="headers to use for names",
        default=["First Name", "Surname"],
        nargs="*",
    )
    parser_generate_heats.add_argument(
        "--heat-size", help="the number of riders in each heat", default=2, type=int
    )
    parser_generate_heats.add_argument(
        "--rounds", help="the number of rounds", default=4, type=int
    )
    parser_generate_heats.set_defaults(func=handle_heats)

    # Generate results
    parser_results = subparsers.add_parser("results")
    parser_results.add_argument(
        "--input", help="input csv rounds list", default="rounds.csv"
    )
    parser_results.add_argument(
        "--output", help="output csv results", default="results.csv"
    )
    parser_results.set_defaults(func=handle_results)

    args = parser.parse_args(args)
    return args


def main():
    args = parse_args(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    args = parse_args(["results", "--input", "results.csv"])
    args.func(args)
