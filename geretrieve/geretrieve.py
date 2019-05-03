#                                                            _
# Ge retrieve ds app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os

# import the Chris app superclass
from chrisapp.base import ChrisApp



class GeRetrieve(ChrisApp):
    """
    An app to retrieve data of interest from GE cloud.
    """
    AUTHORS         = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH        = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC        = os.path.basename(__file__)
    EXECSHELL       = 'python3'
    TITLE           = 'Ge Retrieve'
    CATEGORY        = ''
    TYPE            = 'ds'
    DESCRIPTION     = 'An app to retrieve data of interest from GE cloud'
    DOCUMENTATION   = 'http://wiki'
    VERSION         = '0.1.1'
    LICENSE         = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS = 1  # Override with integer value
    MAX_CPU_LIMIT = ''  # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT = ''  # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}
 
    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """
        self.add_argument('--prefix', dest='prefix', type=str, default='', optional=True,
                          help='retrieve directory/file with this prefix in ge')

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        # get GE cloud prefix
        prefix = options.prefix
        if not prefix: # path passed through CLI has priority over JSON meta file
            prefix = self.load_output_meta()['prefix']
        cmd = 'python {0} -c {1} -p {2} -o {3}'.format('Agent17Download.py',
                                                       'gehc-bch-sdk.config',
                                                       prefix, options.outputdir)
        os.system(cmd)


# ENTRYPOINT
if __name__ == "__main__":
    app = GeRetrieve()
    app.launch()
