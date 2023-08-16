import sys
import math
import csv
import argparse
import random


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="input csv riders list", default="riders.csv")
    parser.add_argument("--output", help="output csv rounds", default="rounds.csv")
    parser.add_argument(
        "--headers",
        help="headers to use for names",
        default=["First Name", "Surname"],
        nargs="*",
    )
    parser.add_argument("--heat-size", help="the number of riders in each heat", default=2, type=int)
    parser.add_argument("--rounds", help="the number of rounds", default=4, type=int)
    args = parser.parse_args(args)
    return args


def load_csv(filename, headers):
    with open(filename) as rider_file:
        rider_reader = csv.DictReader(rider_file)
        riders = []
        for row in rider_reader:
            values = []
            for header in headers:
                value = row[header]
                value = value.strip().title()
                values.append(value)
            riders.append(" ".join(values))
        return riders


def partition(lst, size):
    out = []
    for i in range(0, len(lst), size):
        out.append(lst[i:i+size])
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

def store_csv(output_filename, data):
    with open(output_filename, 'w') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows([] + data)

def main():
    args = parse_args(sys.argv[1:])
    riders = load_csv(args.input, args.headers)
    out_rows = []
    s = set()
    for round in range(args.rounds):
        partition = find_next_heat(riders, s, args)
        s = store_heats_in_set(partition, s)
        for heat in range(0, len(partition)):
            for competitior in partition[heat]:
                out_rows.append({"Round": round+1, "Heat": heat+1, "Competitor": competitior, "Result": 0})
    store_csv(args.output, out_rows)
