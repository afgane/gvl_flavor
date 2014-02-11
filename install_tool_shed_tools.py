"""
A script to automate installation of tool repositories from a Galaxy Tool Shed
into an instance of Galaxy.
Galaxy instance details and the installed tools need to be provided in YAML
format in a file called ``tool_shed_tool_list.yaml``. See
``tool_shed_tool_list.yaml.sample`` for a sample of such a file.

Usage:

    python install_tool_shed_tools.py

"""

import yaml
import datetime as dt
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.toolshed import ToolShedClient
from bioblend.toolshed import ToolShedInstance

tool_list_file = 'tool_shed_tool_list.yaml'
# Load tool list
with open(tool_list_file, 'r') as f:
    tl = yaml.load(f)

gi = GalaxyInstance(tl['galaxy_instance'], tl['api_key'])
r_info = tl['tools']

responses = []

counter = 1
total_num_tools = len(r_info)
default_err_msg = 'All repositories that you are attempting to install have been previously installed.'
for r in r_info:
    if 'install_tool_dependencies' not in r:
        r['install_tool_dependencies'] = True
    if 'install_repository_dependencies' not in r:
        r['install_repository_dependencies'] = True
    if 'tool_shed_url' not in r:
        r['tool_shed_url'] = 'http://toolshed.g2.bx.psu.edu'
    ts = ToolShedInstance(url=r['tool_shed_url'])
    if 'revision' not in r:
        r['revision'] = ts.repositories.get_ordered_installable_revisions(
            r['name'], r['owner'])[-1]

    tsc = ToolShedClient(gi)
    start = dt.datetime.now()
    print '\n(%s/%s) Installing tool %s from %s to section %s' % (counter,
        total_num_tools, r['name'], r['owner'], r['tool_panel_section_id'])
    response = tsc.install_repository_revision(r['tool_shed_url'], r['name'],
        r['owner'], r['revision'], r['install_tool_dependencies'],
        r['install_repository_dependencies'], r['tool_panel_section_id'])
        # new_tool_panel_section_label='API tests')
    end = dt.datetime.now()
    if 'error' in response:
        if response['error'] == default_err_msg:
            print "Tool %s already installed (at revision %s)" % (r['name'], r['revision'])
        else:
            print ("Tool install error! Name: %s, owner: %s, revision: %s, error: %s"
                % (r['name'], r['owner'], r['revision'], response['error']))
    else:
        print "Tool %s installed successfully (in %s) at revision %s" % (r['name'],
            str(end - start), r['revision'])
    outcome = {'tool': r, 'response': response, 'duration': str(end - start)}
    responses.append(outcome)
    counter += 1

# print responses
print "All tools listed in %s have been installed." % tool_list_file
