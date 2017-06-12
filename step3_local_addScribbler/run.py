#! /usr/bin/env python
"""
step3_local_addScribbler/run.py
Use a scribbler to add data to events, and extend step2's event selection
"""

from alphatwirl.binning import Binning, Echo
from alphatwirl.configure import TableConfigCompleter, TableFileNameComposer2
import alphatwirl
from core.completions import complete, to_null_collector_pairs
from core.cut_flows import cut_flow_with_counter
from core.scribblers import  DivideNumpyArrays
import ROOT
import pprint

def main(in_filename, out_dir, tree_name="tree"):
    # Get the input file
    infile = ROOT.TFile.Open(in_filename)
    tree = infile.Get(tree_name)
    if not tree:
        print "Problem getting tree '",tree_name,"' from input file:",in_filename
        return

    # Setup the scribblers to add objects to event
    scribblers = make_scribblers()

    # Prepare the event selection
    event_selection = cut_flow()

    # Describe the output dataframe
    df_cfg=dataframe_config()

    # Run alphatwirl to build the dataframe
    dataframes = summarize(tree, df_cfg, event_selection, scribblers)

    # Print everything out
    print "Number of dataframes created:",len(dataframes)
    for df in dataframes:
        print type(df)
        pprint.pprint(df)


def make_scribblers():
    scribblers = [ 
        DivideNumpyArrays(['mht40_pt', 'met_pt'],'MhtOverMet'),
    ]
    return to_null_collector_pairs(scribblers)


def cut_flow():
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
        'ev : ev.MhtOverMet[0] < 1.25',
    ))

    return cut_flow_with_counter(event_selection, "cut_flow_table.txt")


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


def summarize(tree, df_cfg, event_selection, scribblers, max_events = -1):

    reader_collector_pairs = scribblers + event_selection

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
