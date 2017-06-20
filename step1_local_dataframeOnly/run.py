#! /usr/bin/env python
"""
Produce a dataframe from a local, flat RA1 tree, with columns similar to RA1
bins and unweighted event yields
"""

from alphatwirl.binning import Binning, Echo
from alphatwirl.configure import TableConfigCompleter, TableFileNameComposer2
import alphatwirl
from alphatwirl_interface.completions import complete
import ROOT
import pprint

def main(in_filename, out_dir, tree_name="tree"):
    # Get the input file
    infile = ROOT.TFile.Open(in_filename)
    if not infile or infile.IsZombie():
        return
    tree = infile.Get(tree_name)
    if not tree:
        print "Problem getting tree '",tree_name,"' from input file:",in_filename
        return

    # Describe the output dataframe
    df_cfg=dataframe_config()

    # Run alphatwirl to build the dataframe
    dataframes = summarize(tree, df_cfg)

    # Print everything out
    for df in dataframes:
        pprint.pprint(df)


def dataframe_config():
    # Set up categorical binning 
    htbin = Binning( boundaries=[200, 400, 600, 900, 1200] )
    njetbin = Binning( boundaries=[1, 2, 3, 4, 5, 6] )
    nbjetbin = Echo()

    df_cfg = [
        dict(
            keyAttrNames = ('ht40', 'nJet40', 'nBJet40'),
            keyOutColumnNames = ('htbin', 'njetbin', 'nbjetbin'),
            binnings = (htbin, njetbin, nbjetbin)
        ),
    ]

    return df_cfg


def summarize(tree, df_cfg, max_events = -1):

    reader_collector_pairs = []

    tableConfigCompleter = TableConfigCompleter(
        createOutFileName = TableFileNameComposer2(default_prefix = 'tbl_n')
    )
    reader_collector_pairs += complete( df_cfg, tableConfigCompleter)

    def event_builder():
        return alphatwirl.roottree.BEvents(tree, maxEvents = max_events)

    reader = alphatwirl.loop.ReaderComposite()
    collector = alphatwirl.loop.CollectorComposite()
    for r, c in reader_collector_pairs:
        reader.add(r)
        collector.add(c)
    eventLoop = alphatwirl.loop.EventLoop(event_builder, reader)
    reader = eventLoop()
    return collector.collect(((None, (reader, )), ))


def process_options():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import sys
    import os
    parser = ArgumentParser(description=__doc__, 
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_filename",
                        help="The path to an input data file")
    parser.add_argument("-o", "--out_dir",
                        help="The path to an output directory, which should exist",
                        default=os.getcwd())
    return parser.parse_args()


if __name__ == "__main__":
    args = process_options()
    main(**args.__dict__)
