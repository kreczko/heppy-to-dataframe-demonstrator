#! /usr/bin/env python
"""
step6_weighted_events/run.py
Run over a heppy dataset, weighting events by the genWeight value and
identifying the source sample in the dataframe
"""

from alphatwirl.binning import Binning, Echo
from alphatwirl.configure import TableConfigCompleter, TableFileNameComposer2
from alphatwirl_interface.completions import complete, to_null_collector_pairs
from alphatwirl_interface.cut_flows import cut_flow_with_counter
from alphatwirl_interface.scribblers import  DivideNumpyArrays, ComponentName
from alphatwirl_interface.weighters import  WeightCalculatorProduct
from alphatwirl_interface.heppy.runners import  build_job_manager
import ROOT
import pprint

def main(in_path, out_dir, tree_name="tree", isdata=False):
    # Get the input file
    mgr = build_job_manager(out_dir, in_path, isdata=isdata, n_processes=4,
                            parallel_mode="multiprocessing", force=True)

    # Setup the scribblers to add objects to event
    scribblers = make_scribblers()

    # Prepare the event selection
    event_selection = cut_flow()

    # Describe the output dataframe
    df_cfg=dataframe_config()

    # Run alphatwirl to build the dataframe
    dataframes = summarize(mgr, df_cfg, event_selection, scribblers)

    # Print everything out
    print "Number of dataframes created:",len(dataframes)
    for df in dataframes:
        print type(df)
        pprint.pprint(df)


def make_scribblers():
    scribblers = [
        ComponentName(),
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
    # a category that returns itself and has no next element
    component = Echo(nextFunc=None)

    df_cfg = [
        dict(
            keyAttrNames = ('componentName', 'ht40', 'nJet40', 'nBJet40'),
            keyOutColumnNames = ('component', 'htbin', 'njetbin', 'nbjetbin'),
            binnings = (component, htbin, njetbin, nbjetbin),
            # list of weight branches that are multiplied together for the
            # final event weight
            weight = WeightCalculatorProduct(['genWeight'])
        ),
    ]

    return df_cfg


def summarize(mgr, df_cfg, event_selection, scribblers, max_events = -1):

    reader_collector_pairs = scribblers + event_selection

    tableConfigCompleter = TableConfigCompleter(
        createOutFileName = TableFileNameComposer2(default_prefix = 'tbl_n')
    )
    reader_collector_pairs += complete( df_cfg, tableConfigCompleter)

    # Hard-coded list of components is temporary, need to remove this in the
    # near future
    return mgr.run(reader_collector_pairs,
                   components=["TTWJetsToLNu_amcatnloFXFX", "ZJetsToNuNu_HT100to200_madgraph_ext1"])


def process_options():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import sys
    import os
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_path",
                        help="The path to the input data")
    parser.add_argument("-o", "--out_dir",
                        help="The path to an output directory, which should exist",
                        default=os.getcwd())
    parser.add_argument('--mc', action='store_const', dest='isdata',
                        const=False, default=False, help='Input events are from MC')
    parser.add_argument('--data', action='store_const', dest='isdata',
                        const=True, help='Input events are from Data')
    return parser.parse_args()


if __name__ == "__main__":
    args = process_options()
    main(**args.__dict__)
