# A PySpark script to perform word count on a text file with cleaning.
# This script:
# Reads a text file.
# Cleans the text by removing abbreviations and non-alphabetic characters.
# Tokenizes the text into words.
# Counts the frequency of each word.
# Saves the word counts to an output directory.

import sys
import re
from pyspark.sql import SparkSession

# List of common English abbreviations to remove
ABBREVIATIONS = [
    r'\bMr\.', r'\bMrs\.', r'\bDr\.', r'\bMs\.', r'\bProf\.', r'\bSr\.', r'\bJr\.', r'\bSt\.', r'\bMt\.',
    r'\bi\.e\.', r'\be\.g\.', r'\betc\.', r'\bvs\.', r'\bU\.S\.', r'\bU\.K\.', r'\bA\.M\.', r'\bP\.M\.'
]

def remove_abbreviations(text):
    for abbr in ABBREVIATIONS:
        text = re.sub(abbr, '', text, flags=re.IGNORECASE)
    return text

def tokenize(text):
    text = text.lower()
    text = remove_abbreviations(text)
    text = re.sub(r'[^a-z\s]', '', text)  # remove punctuation/numbers
    return text.split()

def main(input_path, output_path):
    spark = SparkSession.builder.appName("WordCountCleaned").getOrCreate()
    
    # Load input text data
    lines = spark.read.text(input_path).rdd.map(lambda r: r[0])

    # Process and count words
    words = lines.flatMap(tokenize)
    word_counts = words.map(lambda word: (word, 1)) \
                       .reduceByKey(lambda a, b: a + b) \
                       .sortBy(lambda pair: -pair[1])  # Sort by frequency

    # Save output
    word_counts.map(lambda x: f"{x[0]}\t{x[1]}").saveAsTextFile(output_path)

    spark.stop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spark-submit word_count_clean.py <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    main(input_path, output_path)
