#!BPY

"""
Name: 'RealXtend Exporter'
Blender: 249
Group: 'Export'
Tooltip: 'Exports the current scene to RealXtend server'
"""

__author__ = ['Pablo Martin']
__version__ = '0.1'
__url__ = ['B2rex Sim, http://sim.lorea.org',
           'B2rex forum, http://sim.lorea.org/b2rex',
	   'B2rex repo, http://github.com/caedesvvv/b2rex']
__bpydoc__ = "Please see the external documentation that comes with the script."


import b2rexpkg
from b2rexpkg.app import RealxtendExporterApplication


if __name__ == "__main__":
    application = RealxtendExporterApplication()
    application.go()

