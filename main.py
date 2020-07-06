"""
2020 average endgame contribution computer

it should be noted that this sort of task is probably better suited for data downloading
and then querying through something else. for future strategy tools that process data
in a similar way, that's probably a worthwhile improvement (something like sqlite probably?)

I tried to comment the file up for anyone from the team who wants to read it but hopefully
most of it is pretty self-explanatory
"""

import argparse
import tbapy  # you'll need to have this downloaded (in requirements.txt)
import yaml  # you'll need to have this downloaded (in requirements.txt)

# Get team number
# argparse is brought in because it might reduce cross-platform annoyances, not because it's necessary
parser = argparse.ArgumentParser()
parser.add_argument('team', type=int, help='team number')

# TheBlueAlliance wants us to have names like 'frcXXXX', so let's just convert it here
team: str = 'frc{}'.format(parser.parse_args().team)

# this is a Git-ignored file... don't leak your TBA keys!
with open('config.yml', 'r') as fin:
    config = yaml.load(fin, Loader=yaml.BaseLoader)
    tba = tbapy.TBA(config['token'])

endgame_dict = dict()
# {
#   event: { total_score: <>, num_matches: <> }
# }

print('crunching the numbers for {}\'s 2020 endgames!'.format(team))
team_event_keys = tba.team_events(team=team, year=2020, keys=True)
print('Events: {}'.format(team_event_keys))

for event_key in team_event_keys:
    # create space in dictionary
    endgame_dict[event_key] = {'total_score': 0, 'num_matches': 0}

    # find all matches to consider (take all team matches and filter out qualifications only)
    team_all_match_keys = tba.team_matches(team=team, event=event_key, keys=True)

    # create a new list made only of matches whose keys contain the string 'qm'
    # while it reads slightly poorly (sorry), this is a valid way of filtering out elimination matches
    team_qm_keys = list(filter(lambda s: 'qm' in s, team_all_match_keys))

    # store the number of qualification matches they played in in our dictionary
    endgame_dict[event_key]['num_matches'] = len(team_qm_keys)

    for qm_key in team_qm_keys:
        # this gives a TON of data, more than is being used here
        qm_data = tba.match(key=qm_key, simple=False)

        # if you want, uncomment the line below to try looking at all the data you get!
        # print(qm_data)

        # grab alliance and robot number. Then, use those values to grab the robot's "endgame action"
        # this is among the ugliest Python I've ever written, please look away
        alliance = 'blue' if team in qm_data.raw()['alliances']['blue']['team_keys'] else 'red'
        station = 1 + list(qm_data.raw()['alliances'][alliance]['team_keys']).index(team)
        endgame_type = qm_data.raw()['score_breakdown'][alliance]['endgameRobot{}'.format(station)]

        # convert endgame action into point values, add them totals
        if endgame_type == 'Hang':
            endgame_dict[event_key]['total_score'] += 25
        elif endgame_type == 'Park':
            endgame_dict[event_key]['total_score'] += 5

    # now we're done with all the matches for this event, and can move on to the next event
# now we're done with all events


# COMPUTE AVERAGE ENDGAME AND DISPLAY VALUES
for event_name, endgame_data in endgame_dict.items():
    # so many events had 0 matches in 2020 (for obvious reasons), so let's handle this case
    mean_contribution = 0 if endgame_data['num_matches'] == 0 \
        else endgame_data['total_score'] / endgame_data['num_matches']

    print(
        'Team {}\'s average endgame contribution at event {}: {} points ({} matches played)'.format(
            team, event_name, mean_contribution, endgame_data['num_matches']
        )
    )
