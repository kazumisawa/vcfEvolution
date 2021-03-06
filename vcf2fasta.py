# Kazuharu Misawa 2022/05/30
import sys
import vcf
from Bio import SeqIO


def args2target(args):
    target = dict()
    target["reference"] = "GRCh38.fa"
    target["filename"] = args[1]
    target["chrNumber"] = args[2]
    target["chr"] = "chr" + args[2]
    target["start"] = int(args[3])
    target["end"] = int(args[4])
    return target

def withinRange(record, target):
    result = False
    if target["chr"] == record.CHROM:
        currentPos = int(record.POS)
        if (currentPos>=target["start"] ) and (currentPos<=target["end"] ):
            result = True
    return result

def isPhasedOrHomo( genotype ):
    if genotype.phased:
        return True
    if not genotype.is_het:
        return True
    return False

def phasedNucleotide( genotype ):
    if genotype.phased:
        return ( (genotype.gt_bases).split("|") )
    if not genotype.is_het:
        return ( (genotype.gt_bases).split("/") )

def sample2dict(sampleList):
    seq = dict()
    for s in sampleList:
        seq[ s + "_1" ] = ""
        seq[ s + "_2" ] = ""
    return seq

def outputFasta(seq):
    # output
    for title in seq.keys():
        print(">" + title)
        print(seq[title])

def readReference( target ): # load the reference genome
    for record in SeqIO.parse(target["reference"], 'fasta'):
        if record.id == target["chr"]:
            return record.seq

#chromosome and range
target = args2target(sys.argv)
#load the reference genome
targetSeq = readReference(target)
#input vcf
vcf_reader = vcf.Reader(open(target["filename"], 'r'))
#header
sampleList=vcf_reader.samples
seq =  sample2dict(sampleList)
#start of SNPs
nextStart = target["start"]-1 #beginning of sequence
#main loop
for record in vcf_reader:
    if withinRange(record, target):
        #print( record.CHROM, record.POS, alleles(record.REF, record.ALT), end="\t")
        positionOnSequence = record.POS -1
        for s in sampleList:
            genotype = record.genotype(s)
            #print( genotype["GT"], end="\t")
            shared = targetSeq[nextStart:positionOnSequence]
            if isPhasedOrHomo( genotype ) :
                result =  phasedNucleotide( genotype )
            else:
                result = [ record.REF, record.REF]
            seq[ s+"_1" ] = seq[ s+"_1" ] + shared + result[0]
            seq[ s+"_2" ] = seq[ s+"_2" ] + shared + result[1]
            maxLen = len(record.REF)
            nextStart = positionOnSequence + maxLen # start of the next sequence


#output
outputFasta(seq)
