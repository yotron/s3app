import argparse
import sys


class S3ServerAroParser:
    parser = argparse.ArgumentParser

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        sys.exit(2)

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Start parameter for the S3App web server.')
        self.parser.add_argument('-s', '--host', type=str,
                          help='Listener Host IP. Default: 0.0.0.0')
        self.parser.add_argument('-p', '--port', type=int,
                          help='Listener Host Port.  Default: 8080.')
        self.parser.add_argument('-t', '--threads', type=int,
                          help='Threads for parallelization. Default: 4.')


    def getKw(self, args):
        kw = {}
        for arg in vars(args):
            if getattr(args, arg) is not None:
                kw[arg] = getattr(args, arg)
        return kw