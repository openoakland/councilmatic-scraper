import pickle

def load_jurisdiction():
    #juris = pickle.load( open( "tests/data/juris/juris.p", "rb" ) )
    juris = pickle.load( open( "data/juris/juris.p", "rb" ) )
    print("###load_jurisdiction:", juris)

    return juris
