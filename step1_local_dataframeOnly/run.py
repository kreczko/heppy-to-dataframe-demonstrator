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


def main(in_path, out_dir, tree_name="tree"):
    # Get the input file
    infile = ROOT.TFile.Open(in_path)
    if not infile or infile.IsZombie():
        return
    tree = infile.Get(tree_name)
    if not tree:
        print "Problem getting tree '", tree_name, "' from input file:", in_path
        return

    # Describe the output dataframe
    df_cfg = dataframe_config()

    # Run alphatwirl to build the dataframe
    dataframes = summarize(tree, df_cfg)

    # Print everything out
    for df in dataframes:
        pprint.pprint(df)


def dataframe_config():
    '''
        Creates the definition/config of the data frame (DF).

        :return a list of DF configs
    '''
    # Set up categorical binning
    # use simple binning for HT and N_jet
    htbin = Binning(boundaries=[200, 400, 600, 900, 1200])
    njetbin = Binning(boundaries=[1, 2, 3, 4, 5, 6])
    # Echo simply returns the value it gets
    nbjetbin = Echo()
    # explicit version
    # nbjetbin = Echo(nextFunc = lambda x: x+1, valid = lambda x: True)

    # a list of DF configs
    df_configs = [
        dict(
            # which tree branches to read in
            keyAttrNames=('ht40', 'nJet40', 'nBJet40'),
            # which columns in the DF they should be mapped to
            keyOutColumnNames=('htbin', 'njetbin', 'nbjetbin'),
            # the binning for the categories
            binnings=(htbin, njetbin, nbjetbin)
        ),
    ]

    return df_configs


def summarize(tree, df_cfg, max_events=-1):
    '''
        Summarise the data in the tree into the data frames (DFs) given in
        df_cfg.

        :param tree(ROOT.TTree): the input tree
        :param df_cfg(list): list of DF definitions
        :param max_events(int): Number of events to process.
                                Default is -1 -> all events
    '''

    reader_collector_pairs = []

    # setting up defaults to complete the provided DF configs
    tableConfigCompleter = TableConfigCompleter(
        # using a composer to create a predictable output file name
        # based on the names of the output columns
        createOutFileName=TableFileNameComposer2(default_prefix='tbl_n')
    )
    # combine configs and completers
    reader_collector_pairs += complete(df_cfg, tableConfigCompleter)

    # wrap tree for the event loop
    def event_builder():
        return alphatwirl.roottree.BEvents(tree, maxEvents=max_events)

    # create reader and collector collections
    reader = alphatwirl.loop.ReaderComposite()
    collector = alphatwirl.loop.CollectorComposite()
    for r, c in reader_collector_pairs:
        reader.add(r)
        collector.add(c)

    # loop over all events
    eventLoop = alphatwirl.loop.EventLoop(event_builder, reader)
    reader = eventLoop()

    # collect all results and return them
    return collector.collect(((None, (reader, )), ))


def process_options():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import sys
    import os
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_path",
                        help="The path to an input data")
    parser.add_argument("-o", "--out_dir",
                        help="The path to an output directory, which should exist",
                        default=os.getcwd())
    return parser.parse_args()


if __name__ == "__main__":
    args = process_options()
    main(**args.__dict__)
