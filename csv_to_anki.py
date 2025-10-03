#!/usr/bin/env python
"""
Convert csv file containing japanese words with readings to anki deck

Aside from just generating anki decks, this is useful for importing (kanji)
words with their correct kana readings into jpdb. Otherwise when directly
importing from text, the parser might be confused between words using the
same kanji with different readings.

It will also split decks into 10000 words each as that is the max for jpdb decks

To use,
"""

import sys
import csv
from itertools import islice
from collections import defaultdict
import re
import json
from typing import List, Dict, DefaultDict, Set, Iterable
import argparse
import genanki


debug = False


def main(
    filename: str,
    word: str,
    reading: str,
    delimiter: str,
    batch_size: int,
    save_path: str,
    save_dir: str,
) -> None:
    MODEL_ID = 1656946912  # hard-coded "random" id
    deck_id = 1676571463

    model = genanki.Model(
        MODEL_ID,
        "Word/Reading Model",
        fields=[
            {"name": "Word"},
            {"name": "Reading"},
        ],
        templates=[
            {
                "name": "Card",
                "qfmt": "{{Word}}",  # front of card
                "afmt": '{{FrontSide}}<hr id="answer">{{Reading}}',  # back of card
            },
        ],
    )

    # read csv and batch into batch_size rows each
    batches = []
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        while True:
            batch = list(islice(reader, batch_size))
            if not batch:
                break
            batches.append(batch)

    # create decks for each batch
    decks = []
    for batch in batches:
        deck = genanki.Deck(deck_id, "Word/Reading")
        deck_id += 1
        for row in batch:
            note = genanki.Note(model=model, fields=[row[word], row[reading]])
            deck.add_note(note)
        decks.append(deck)

        if debug:
            print(*deck.notes[:1], sep="\n")

    # save decks to .apkg files
    for i, deck in enumerate(decks):
        output_path = f"{save_dir}/{save_path.replace('.apkg', f'_{i}.apkg')}"
        genanki.Package(deck).write_to_file(output_path)

        if debug:
            print(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert csv file containing words with readings to anki deck"
    )
    parser.add_argument(
        "input_file",
        type=str,
        default="words.csv",
        nargs="?",
        help="path to input csv file (default 'words.csv')",
    )
    parser.add_argument(
        "-w",
        "--word",
        type=str,
        default="word",
        help="word column name (default 'word')",
    )
    parser.add_argument(
        "-r",
        "--reading",
        type=str,
        default="reading",
        help="reading column name (default 'reading')",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default=",",
        help="csv delimiter (default ','). for ease of use, you can enter 'tab' or '\\t' for tab delimiter",
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default="10000",
        help="max batch size per anki deck (default 10000). input 0 to save everything into a single deck",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        nargs="?",
        default="output.apkg",
        help="path to output file (default 'output.apkg')",
    )
    parser.add_argument(
        "-O",
        "--output_dir",
        type=str,
        nargs="?",
        default="output",
        help="path to output dir (default 'output/')",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="if set, enable debug prints",
    )
    args = parser.parse_args()
    debug = args.debug
    if debug:
        print(args)

    # set input file based on if user specified file name
    input_file = args.input_file
    word_column = args.word
    reading_column = args.reading
    delim = "\t" if args.delimiter in ("tab", "\\t") else args.delimiter
    batchsize = sys.maxsize if args.batch_size == 0 else args.batch_size
    output_file = args.output_file
    output_dir = args.output_dir
    if debug:
        print(
            input_file,
            word_column,
            reading_column,
            delim and delim.encode(),
            batchsize,
            output_file,
            output_dir,
        )

    main(
        input_file,
        word_column,
        reading_column,
        delim,
        batchsize,
        output_file,
        output_dir,
    )
