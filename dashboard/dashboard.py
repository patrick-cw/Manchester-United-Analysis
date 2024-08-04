import streamlit as st
import pandas as pd
from mplsoccer import Pitch
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter


# Progressive passes aim to capture this and are defined as “completed open-play passes in the attacking two-thirds of the pitch that move the ball at least 25% closer to the goal
def is_progressive_pass(row):
    pitch_length = 100  # Length of the pitch in meters
    goal_width = 7.32  # Standard goal width in meters
    attacking_two_thirds_start = pitch_length / 3  # 33.33 meters from the goal
    
    # Closest y position on the goal line
    closest_y_on_goal = min(max(row['y'], (50 - goal_width / 2)), (50 + goal_width / 2))
    closest_y_on_goal_end = min(max(row['end_y'], (50 - goal_width / 2)), (50 + goal_width / 2))
    
    # Calculate initial and final distances to the closest point on the goal line
    initial_distance_to_goal = ((pitch_length - row['x'])**2 + (closest_y_on_goal - row['y'])**2)**0.5
    final_distance_to_goal = ((pitch_length - row['end_x'])**2 + (closest_y_on_goal_end - row['end_y'])**2)**0.5
    
    return (row['x'] > attacking_two_thirds_start and 
            row['end_x'] > row['x'] and 
            final_distance_to_goal <= initial_distance_to_goal * 0.75)

scaling_factor = 0.5
def plot_shot_map(playerName):
    filter_event = player_events.loc[(player_events['period_display_name']!='PenaltyShootout') & (player_events.x>=50.0)].reset_index(drop=True)
    
    shot_goal = filter_event.loc[filter_event['type_display_name']=="Goal"].reset_index(drop=True)
    saved_shot = filter_event.loc[filter_event['type_display_name']=="SavedShot"].reset_index(drop=True)
    missed_shot = filter_event.loc[filter_event['type_display_name']=="MissedShots"].reset_index(drop=True)

    # Set up the pitch
    goal_count = len(shot_goal.index)
    saved_shot_count = len(saved_shot.index)
    missed_shot_count = len(missed_shot.index)
    shots_count = goal_count + saved_shot_count + missed_shot_count
    try:
        shot_rate = round(goal_count/shots_count *100,2)
    except ZeroDivisionError:
        shot_rate = 0
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(saved_shot.x, saved_shot.y, s=70*scaling_factor, c = '#77c3ec', zorder=3, ax=ax,edgecolors="black",label='Saved')
    pitch.scatter(missed_shot.x, missed_shot.y, s=50*scaling_factor, c = '#ba4f45', zorder=3, ax=ax,edgecolors="black",label='Missed')
    pitch.scatter(shot_goal.x, shot_goal.y, s=100*scaling_factor, c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Goals')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Shot Map', fontsize=20*scaling_factor, color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{shots_count} Total Shots', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{shot_rate}% Conversion Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.37, 1, f'{goal_count} Goals', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.46, 1, f'{saved_shot_count} Saved', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#77c3ec')
    ax.text(0.55, 1, f'{missed_shot_count} Missed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')

    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes,fontdict={'size':12*scaling_factor,'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes,fontdict={'size':12*scaling_factor,'color':'white'})

    st.pyplot(fig, use_container_width=True)

# Plot Aerial Map
def plot_aerial_map(playerName):
    # Aerial
    aerial_success = aerial_events.loc[aerial_events.outcome_type_display_name=='Successful']
    aerial_fail = aerial_events.loc[aerial_events.outcome_type_display_name=='Unsuccessful']

    aerial_success_count = len(aerial_success.index)
    aerial_fail_count = len(aerial_fail.index)
    try:
        aerial_rate = round(aerial_success_count/(aerial_success_count + aerial_fail_count) *100,2)
    except ZeroDivisionError:
        aerial_rate = 0
    
    # Draw the Pitch
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(aerial_fail.x, aerial_fail.y, s=50*scaling_factor,marker='o', c = '#ba4f45', zorder=3, ax=ax,edgecolors="black",label='Unsuccessful Aerial Duel')
    pitch.scatter(aerial_success.x, aerial_success.y, s=100*scaling_factor,marker='o', c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Successful Aerial Duel')
    
    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Aerial Duel Map', fontsize=20*scaling_factor,color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{aerial_success_count} Total Aerial Duels', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{aerial_rate}% Success Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.38, 1, f'{aerial_success_count} Successful', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.5, 1, f'{aerial_fail_count} Unsuccessful', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

#Plot Clearance Map
def plot_clearance_map(playerName):
    clearance_success = clearance_events.loc[clearance_events.outcome_type_display_name=='Successful']
    clearance_success_count = len(clearance_success.index)
    
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(clearance_success.x, clearance_success.y, s=100*scaling_factor,marker='D', c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Clearance')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper right')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Clearance Map', fontsize=20*scaling_factor,color='white', pad=20*scaling_factor)
    ax.text(0.5, 1, f'{clearance_success_count} Total Clearances', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})

    st.pyplot(fig, use_container_width=True)

#Plot Recovery map
def plot_recovery_map(playerName):
    # Recovery
    recovery_success = recovery_events.loc[recovery_events.outcome_type_display_name=='Successful']
    recovery_success_count = len(recovery_success.index)
    
    # Draw the Pitch
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(recovery_success.x, recovery_success.y, s=140*scaling_factor,marker='X', c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Ball Recovery')
    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper right')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Ball Recovery Map', fontsize=20*scaling_factor,color='white', pad=20*scaling_factor)
    ax.text(0.5, 1, f'{recovery_success_count} Total Ball Recoveries', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

#Plot take on map
def plot_take_on_map(playerName):
    to_success = take_on_events.loc[take_on_events.outcome_type_display_name=='Successful']
    to_fail = take_on_events.loc[take_on_events.outcome_type_display_name=='Unsuccessful']

    # Set up the pitch
    to_success_count = len(to_success.index)
    to_fail_count = len(to_fail.index)
    try:
        to_rate = round(to_success_count/(to_fail_count + to_success_count) *100,2)
    except ZeroDivisionError:
        to_rate = 0
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(to_fail.x, to_fail.y, s=50*scaling_factor, c = '#ba4f45', zorder=3, ax=ax,edgecolors="black",label='Unsuccessful')
    pitch.scatter(to_success.x, to_success.y, s=100*scaling_factor, c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Successful')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Take On Map', fontsize=20*scaling_factor,color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{to_success_count + to_fail_count} Total Take On', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{to_rate}% Success Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.38, 1, f'{to_success_count} Successful', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.5, 1, f'{to_fail_count} Unsuccessful', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)


#Plot tackle map
def plot_tackle_map(playerName):
    tackle_success = tackle_events.loc[tackle_events.outcome_type_display_name=='Successful']
    tackle_fail = tackle_events.loc[tackle_events.outcome_type_display_name=='Unsuccessful']

    # Set up the pitch
    tackle_success_count = len(tackle_success.index)
    tackle_fail_count = len(tackle_fail.index)
    try:
        tackle_rate = round(tackle_success_count/(tackle_fail_count + tackle_success_count) *100,2)
    except ZeroDivisionError:
        tackle_rate = 0
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(tackle_fail.x, tackle_fail.y, s=80*scaling_factor, marker='X', c = '#ba4f45', zorder=3, ax=ax,edgecolors="black",label='Unsuccessful')
    pitch.scatter(tackle_success.x, tackle_success.y, s=140*scaling_factor, marker='X', c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Successful')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Tackle Map', fontsize=20*scaling_factor,color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{tackle_success_count + tackle_fail_count} Total Tackle', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{tackle_rate}% Success Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.38, 1, f'{tackle_success_count} Successful', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.5, 1, f'{tackle_fail_count} Unsuccessful', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

#Plot Interception Map
def plot_interception_map(playerName):
    interception_success = interception_events.loc[interception_events.outcome_type_display_name=='Successful']
    interception_success_count = len(interception_success.index)
    
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    pitch.scatter(interception_success.x, interception_success.y, s=100*scaling_factor,marker='o', c = '#2eb774', zorder=3, ax=ax,edgecolors="black",label='Clearance')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper right')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Interception Map', fontsize=20*scaling_factor,color='white', pad=20*scaling_factor)
    ax.text(0.5, 1, f'{interception_success_count} Total Interceptions', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

#Plot Pass Map
def plot_pass_map(playerName):
    pass_success = passing.loc[passing.outcome_type_display_name=='Successful']
    pass_fail = passing.loc[passing.outcome_type_display_name=='Unsuccessful']

    # Set up the pitch
    pass_success_count = len(pass_success.index)
    pass_fail_count = len(pass_fail.index)
    try:
        pass_rate = round(pass_success_count/(pass_success_count + pass_fail_count) *100,2)
    except ZeroDivisionError:
        pass_rate = 0
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    # Plot the completed passes
    pitch.arrows(pass_success.x, pass_success.y,
                pass_success.end_x, pass_success.end_y, width=1.5*scaling_factor,
                headwidth=3, headlength=3, color='#2eb774', ax=ax, label='Completed Pass')

    # Plot the other passes
    pitch.arrows(pass_fail.x, pass_fail.y,
                pass_fail.end_x, pass_fail.end_y, width=1*scaling_factor,
                headwidth=3, headlength=3, headaxislength=10*scaling_factor,
                color='#ba4f45', ax=ax, label='Failed Pass')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')
    #fig.text(0.15, 0.65, f'{pass_success_count} Completed', ha='left', va='baseline', fontsize=11, color='#2eb774')
    #fig.text(0.15, 0.62, f'{pass_fail_count} Failed', ha='left', va='baseline', fontsize=11, color='#ba4f45')
    #fig.text(0.14, 0.61, f'{pass_rate}%', ha='left', va='baseline', fontsize=11, color='white')
    # Set the title
    ax_title = ax.set_title(f'{playerName} Pass Map', fontsize=20*scaling_factor,color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{pass_success_count + pass_fail_count} Total Passes', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{pass_rate}% Completion Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.385, 1, f'{pass_success_count} Completed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.525, 1, f'{pass_fail_count} Failed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

# Plot Progressive Pass Map
def plot_progressive_pass_map(playerName):
    passing['is_progressive'] = passing.apply(is_progressive_pass, axis=1)
    progressive_pass = passing[passing['is_progressive']].reset_index(drop=True)
    progressive_pass_success = progressive_pass.loc[progressive_pass.outcome_type_display_name=='Successful']
    progressive_pass_fail = progressive_pass.loc[progressive_pass.outcome_type_display_name=='Unsuccessful']
    # Set up the pitch
    progressive_pass_success_count = len(progressive_pass_success.index)
    progressive_pass_fail_count = len(progressive_pass_fail.index)
    try:
        progressive_pass_rate = round(progressive_pass_success_count/(progressive_pass_success_count + progressive_pass_fail_count) *100,2)
    except ZeroDivisionError:
        progressive_pass_rate = 0
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    # Plot the completed passes
    pitch.arrows(progressive_pass_success.x, progressive_pass_success.y,
                progressive_pass_success.end_x, progressive_pass_success.end_y, width=1.5*scaling_factor,
                headwidth=3, headlength=3, color='#2eb774', ax=ax, label='Completed Pass')

    # Plot the other passes
    pitch.arrows(progressive_pass_fail.x, progressive_pass_fail.y,
                progressive_pass_fail.end_x, progressive_pass_fail.end_y, width=1*scaling_factor,
                headwidth=3, headlength=3, headaxislength=10*scaling_factor,
                color='#ba4f45', ax=ax, label='Failed Pass')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Progressive Pass Map', fontsize=20*scaling_factor,color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{progressive_pass_success_count + progressive_pass_fail_count} Progressive Passes', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{progressive_pass_rate}% Completion Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.385, 1, f'{progressive_pass_success_count} Completed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.52, 1, f'{progressive_pass_fail_count} Failed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')

    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

# Plot Forward Pass Map
def plot_forward_pass_map(playerName):
    forward_pass = passing.loc[passing.end_x>passing.x+1]
    forward_pass_success = forward_pass.loc[forward_pass.outcome_type_display_name=='Successful']
    forward_pass_fail = forward_pass.loc[forward_pass.outcome_type_display_name=='Unsuccessful']
    forward_pass_success_count = len(forward_pass_success.index)
    forward_pass_fail_count = len(forward_pass_fail.index)
    try:
        forward_pass_rate = round(forward_pass_success_count/(forward_pass_success_count + forward_pass_fail_count) *100,2)
    except ZeroDivisionError:
        forward_pass_rate = 0
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    # Plot the completed passes
    pitch.arrows(forward_pass_success.x, forward_pass_success.y,
                forward_pass_success.end_x, forward_pass_success.end_y, width=1.5*scaling_factor,
                headwidth=3, headlength=3, color='#2eb774', ax=ax, label='Completed Pass')

    # Plot the other passes
    pitch.arrows(forward_pass_fail.x, forward_pass_fail.y,
                forward_pass_fail.end_x, forward_pass_fail.end_y, width=1*scaling_factor,
                headwidth=3, headlength=3, headaxislength=10*scaling_factor,
                color='#ba4f45', ax=ax, label='Failed Pass')

    # Set up the legend
    ax.legend(facecolor='white', handlelength=1*scaling_factor, edgecolor='None', fontsize=12*scaling_factor, loc='upper left')

    # Set the title
    ax_title = ax.set_title(f'{playerName} Forward Pass Map', fontsize=20*scaling_factor,color='white', pad=50*scaling_factor)
    ax.text(0.5, 1.08, f'{forward_pass_success_count + forward_pass_fail_count} Forward Passes', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')
    ax.text(0.5, 1.04, f'{forward_pass_rate}% Completion Rate', ha='center', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='white')
    ax.text(0.385, 1, f'{forward_pass_success_count} Completed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#2eb774')
    ax.text(0.52, 1, f'{forward_pass_fail_count} Failed', ha='left', va='center', transform=ax.transAxes, fontsize=10*scaling_factor, color='#ba4f45')

    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(.99, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 
    st.pyplot(fig, use_container_width=True)

# Plot Receive Pass Map
def plot_receive_pass_map(playerName):
    # Initialize pitch
    pitch = Pitch(pitch_type='opta', half=False, line_zorder=2,
                  pitch_color='#22312b', line_color='#efefef')
    fig, ax = pitch.draw(figsize=(6, 4))
    fig.set_facecolor('#22312b')

    # Calculate statistics for the heatmap
    rp_count = len(receive_pass.index)
    bin_statistic = pitch.bin_statistic(receive_pass.end_x, receive_pass.end_y, statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)

    # Plot heatmap
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')

    # Add title and subtitle
    ax_title = ax.set_title(f'{playerName} Receive Pass Heatmap', fontsize=20*scaling_factor, color='white', pad=20*scaling_factor)
    ax.text(0.5, 1, f'{rp_count} Passes Received', ha='center', va='center', transform=ax.transAxes, fontsize=14*scaling_factor, color='white')

    # Customize colorbar
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.6)
    cbar.outline.set_edgecolor('#efefef')
    cbar.ax.yaxis.set_tick_params(color='#efefef')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')

    # Add footer text
    ax.text(-.01, -.02, 'Data: Opta', ha='left', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'})
    ax.text(1.1, -.02, 'Twitter:@patrickcw_', ha='right', va='bottom', transform=ax.transAxes, fontdict={'size':12*scaling_factor, 'color':'white'}) 

    st.pyplot(fig, use_container_width=True)

st.title("Manchester United Dashboard")

all_events_2023 = pd.read_csv('data/Manchester United Events 2023-2024 Preprocessed.csv',index_col=0)
player_list_2023 = all_events_2023[['player_name','player_id']]
player_list_2023 = player_list_2023.drop_duplicates().dropna().sort_values('player_name').reset_index(drop=True)
player_stats_2023 = pd.read_csv('data/Manchester United 2023 - 2024 Player Stats.csv',index_col=0)
all_events_2022 = pd.read_csv('data/Manchester United Events 2022-2023 Preprocessed.csv',index_col=0)
player_list_2022 = all_events_2022[['player_name','player_id']]
player_list_2022 = player_list_2022.drop_duplicates().dropna().sort_values('player_name').reset_index(drop=True)
player_stats_2022 = pd.read_csv('data/Manchester United 2022 - 2023 Player Stats.csv',index_col=0)
# Sidebar for user input
st.sidebar.title("Selection")

# Sidebar options
season_option = st.sidebar.selectbox(
    "Select Season",
    ("2022-2023", "2023-2024"),index=1
)

# type_option = st.sidebar.selectbox(
#     "Select Team or Player",
#     ("Team", "Player")
# )
if season_option=="2023-2024":
    player_option = st.sidebar.selectbox(
        "Select Player Name",
        player_list_2023['player_name']
    )
    
    playerName=player_option
    interception_events = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='Interception')].reset_index(drop=True)
    tackle_events = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='Tackle')].reset_index(drop=True)
    take_on_events = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='TakeOn')].reset_index(drop=True)
    passing = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='Pass')].reset_index(drop=True)
    receive_pass = all_events_2023.loc[all_events_2023.pass_recipient_name==f'{playerName}'].reset_index(drop=True)
    player_events = all_events_2023.loc[all_events_2023.player_name==f'{playerName}'].reset_index(drop=True)
    clearance_events = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='Clearance')].reset_index(drop=True)
    aerial_events = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='Aerial')].reset_index(drop=True)
    recovery_events = all_events_2023.loc[(all_events_2023.player_name==f'{playerName}')&(all_events_2023.type_display_name=='BallRecovery')].reset_index(drop=True)
    player_stat = player_stats_2023.loc[player_stats_2023.Player==f'{playerName}'].reset_index(drop=True)
    
elif season_option=="2022-2023":
    player_option = st.sidebar.selectbox(
        "Select Player Name",
        player_list_2022['player_name']
    )
    playerName=player_option
    interception_events = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='Interception')].reset_index(drop=True)
    tackle_events = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='Tackle')].reset_index(drop=True)
    take_on_events = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='TakeOn')].reset_index(drop=True)
    passing = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='Pass')].reset_index(drop=True)
    receive_pass = all_events_2022.loc[all_events_2022.pass_recipient_name==f'{playerName}'].reset_index(drop=True)
    player_events = all_events_2022.loc[all_events_2022.player_name==f'{playerName}'].reset_index(drop=True)
    clearance_events = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='Clearance')].reset_index(drop=True)
    aerial_events = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='Aerial')].reset_index(drop=True)
    recovery_events = all_events_2022.loc[(all_events_2022.player_name==f'{playerName}')&(all_events_2022.type_display_name=='BallRecovery')].reset_index(drop=True)
    player_stat = player_stats_2022.loc[player_stats_2022.Player==f'{playerName}'].reset_index(drop=True)

# Display selected option in the main area
st.write(f"You selected: {season_option} Season")
st.write(f"Full Player Stats")
if season_option == "2022-2023":
    st.dataframe(player_stats_2022.set_index(player_stats_2022.columns[0]))
elif season_option == "2023-2024":
    st.dataframe(player_stats_2023.set_index(player_stats_2023.columns[0]))

st.write(f"{playerName} Stats")
st.dataframe(player_stat.set_index(player_stat.columns[0]))
plot_shot_map(playerName)
plot_take_on_map(playerName)
plot_receive_pass_map(playerName)
plot_pass_map(playerName)
plot_progressive_pass_map(playerName)
plot_forward_pass_map(playerName)
plot_aerial_map(playerName)
plot_clearance_map(playerName)
plot_recovery_map(playerName)
plot_interception_map(playerName)
plot_tackle_map(playerName)