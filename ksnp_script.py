#!/usr/bin/env python3

# script to run kSNP on assembled sequences
# command ./ksnp_script.py -i /path/to/directory/having/contig_sequence/sub_directories -o /path/to/output/directory -c core[optional; by default = 1] 

import subprocess
import sys
import re
import argparse
import os


parser = argparse.ArgumentParser(description="Skesa Genome Assembly")
parser.add_argument("-i", "--inputpath", help="path to the directory that has all the assembled genomes as sub-directories", required=True)
parser.add_argument("-o", "--outputpath", help="path to the directory that will store the results", required=True)
parser.add_argument("-c", "--cores", help="number of cores; by default = 1", type=str, default="1")


args = parser.parse_args()


# Creating a kSNP input file contaning the list of genome sequence paths tab separated with genomeID
ksnp_input_file_name = "in_list.txt"
in_list_file_path = os.path.join(args.outputpath, ksnp_input_file_name)
with open(in_list_file_path, "w") as fp: # creates a file named in_list.txt at the args.outputpath location
    for genome_dir in os.listdir(args.inputpath): # to read each genome sequence directory
        fp.write(args.inputpath+"/"+genome_dir+"/"+"contigs.fasta")
        fp.write("\t")
        fp.write(genome_dir) # writing the name of genome_dir in the list file as the contigs file have the same name for all sequences
        fp.write("\n")


# Creating a combined fasta file to be used as input for MakeFasta utility
# MakeFasta combines all fasta files into one file to be used as input for next step (Kchooser)
combine_fasta_loc = args.outputpath+"/"+"comb_fasta.fasta"
subprocess.call(["MakeFasta", in_list_file_path, combine_fasta_loc])

# Finding optimal k-mer using Kchooser utility
subprocess.call(["Kchooser", combine_fasta_loc])

#Reading Kchooser.report file to find the optimum K-mer value
with open("Kchooser.report", "r") as fp:
    lines = fp.readlines() # entire file read as a list named lines

opt_k = lines[4][26:28] # finding the optimum k which is at line 5 of Kchooser.report
fck = lines[14][6:11] # finding FCK value from Kchooser.report file

#Remove combine_fasta file. Path is combine_fasta_loc
subprocess.call(["rm", combine_fasta_loc])

# Running kSNP
subprocess.call(["kSNP3", "-in", in_list_file_path, "-outdir", args.outputpath, "-k", opt_k, "-ML", "-NJ", "-CPU", args.cores])

print ("FCK value =", fck)

