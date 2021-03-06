#!/usr/bin/env python

import sys
import argparse

def add_options(main_parser):
    pass

def generate_final_gff(input_files, output):
    hits = {}
    outfd = open(output, "w") if output else sys.stdout
    if not input_files: input_files = [None]
    for f in input_files:
        handle = open(f) if f else sys.stdin
        for l in handle:
            if l.startswith("#"):
                continue
            fs = l.rstrip().split("\t")
            fs[1] = "BreakSeq"
            jid = tuple(fs[0:5])
            ct = int(fs[5])
            j = ord(fs[7]) - ord('A')
            if jid not in hits:
                hits[jid] = [0, 0, 0, 0, 0]
            hits[jid][j] += ct
            pe = [t.split(" ")[-1] for t in fs[-1].split(";") if t.find("PE ") == 0][0]
            length = int([t.split(" ")[-1] for t in fs[-1].split(";") if t.find("SVLEN ") == 0][0])
            hits[jid][3] += 1 if pe == 'Y' else 0
            hits[jid][4] = length

    for jid, hit in hits.items():
        tscore = (sum(hit[:-1])) / 2
        qual = "LowQual"
        if tscore >= 2:
            qual = "PASS2" if hit[3] > 0 else "PASS1"
        outfd.write('%s\t%s\t.\t.\tQUAL %s;ABC %s,%s,%s;PE %s;SVLEN %s\n' % ("\t".join(jid), tscore, qual, hit[0], hit[1], hit[2], hit[3], hit[4]))
    if output:
        outfd.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate final list of calls in GFF", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_options(parser)
    parser.add_argument("--input", help="GFF generated by breakseq_core. Leave unspecified for stdin", nargs="+", default=[])
    parser.add_argument("--output", help="Final GFF. Leave unspecified for stdout")

    args = parser.parse_args()
    generate_final_gff(args.input, args.output)