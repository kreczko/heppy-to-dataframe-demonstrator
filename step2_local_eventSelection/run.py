#! /usr/bin/env python
"""
step2_local_eventSelection/run.py
Add event selection to process, building from step1_local_dataframeOnly/run.py
"""

from alphatwirl.binning import Binning, Echo
from alphatwirl.configure import TableConfigCompleter, TableFileNameComposer2
import alphatwirl
from alphatwirl_interface.completions import complete
from alphatwirl_interface.cut_flows import cut_flow_with_counter
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

    # Prepare the event selection
    event_selection = cut_flow()

    # Describe the output dataframe
    df_cfg = dataframe_config()

    # Run alphatwirl to build the dataframe
    dataframes = summarize(tree, df_cfg, event_selection)

    # Print everything out
    for df in dataframes:
        pprint.pprint(df)


def cut_flow():
    '''
        Defines all cuts that will be applied to input data
    '''
    # dictionary of selection criteria
    # the 'All' key denotes that an event has to pass all the listed cuts
    # other options are Any (or) and Not (inverse)
    # event (`ev`) refers to a single entry in the input tree
    # names and indices after that are the branch names
    event_selection = dict(All = (
        'ev : ev.cutflowId[0] == 1',
        'ev : ev.nIsoTracksVeto[0] <= 0',
        'ev : ev.nJet40[0] >= 2',
        'ev : ev.ht40[0] >= 200',
        'ev : ev.nJet100[0] >= 1',
        'ev : ev.nJet40failedId[0] == 0',
        'ev : ev.nJet40Fwd[0] == 0',
        'ev : -2.5 < ev.jet_eta[0] < 2.5',
        'ev : 0.1 <= ev.jet_chHEF[0] < 0.95',
        'ev : 130 <= ev.mht40_pt[0]',
    ))
    # These would be nice, but they require scribblers; we add these in step3
    #    'ev : ev.MhtOverMet[0] < 1.25',

    # create a reader + collector pair for the cutflow
    # the collector will reject events and store the cut flow into a text file
    return cut_flow_with_counter(event_selection, "cut_flow_table.txt")


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


def summarize(tree, df_cfg, event_selection, max_events = -1):
    '''
        Summarise the data in the tree into the data frames (DFs) given in
        df_cfg.

        :param tree(ROOT.TTree): the input tree
        :param df_cfg(list): list of DF definitions
        :param event_selection: pairs of event selections and collectors
        :param max_events(int): Number of events to process.
                                Default is -1 -> all events
    '''

    reader_collector_pairs = event_selection

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
