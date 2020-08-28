# Built-in libraries
import re

# Pipy libraries
import numpy as np
import csv

# Useful functions
def safe_float(var):
	var = var.upper()
	if var == '' or 'nan' in str.lower(var):
		return np.NAN
	else:
		try:
			return float(var)
		except ValueError:
			return var

# Splits the string using mulitple delimiters and remove quotes
def autosplit(string, pp=None):
	string = string.replace('"','').replace('\'', '')
	string = [s for s in re.split(',|;| |\t|\|', string) if s != '']
	if pp is not None:
		string = list(map(pp, string))
	return string

# Read a CSV file and sniff it to automatically find the delimiter (header treaded as normal data)
def csv_read(filepath, sniff=True, pp=None, delimiters=None):
	with open(filepath, 'r', newline='') as f:
		try:
			dialect = csv.Sniffer().sniff(f.read(2048))
			f.seek(0)
			reader = csv.reader(f, dialect=dialect)
		except csv.Error:
			f.seek(0)
			reader = csv.reader(f, delimiter=delimiters)
		if pp is None:
			contents = list(reader)
		else:
			contents = [list(map(pp, row)) for row in reader]
	return contents

# Writes a csv file
def csv_write(filepath, data, header=None, delimiter=';'):
	with open(filepath, 'w', newline='') as f:
		writer = csv.writer(f, delimiter=delimiter)
		if header is not None:
			writer.writerow(header)
		writer.writerows(data)

# Generate a neat table for viewing the results
def results_table(inputs, outputs, data):
	results = {'Variable':list(outputs), 'Actual':[], 'Target':[], 'Err.abs':[], 'Err.rel (%)':[]}
	for i in range(len(outputs)):
		offset = 1 + len(inputs) + 4*i
		results['Actual'].append(data[offset])
		results['Target'].append(data[offset+1])
		results['Err.abs'].append(data[offset+2])
		results['Err.rel (%)'].append(data[offset+3]*100)
	return results

# Generate parasite plots that share y and x axes
# def multiplot(fig, side, *args, **kwargs):
# 	"""
# 	This function adds parasite axis to an already existing plot. If using a figure
# 	that has multiple subplots, all subplots must be created at the beginning of the figure generation.
# 	Valid parameters are:
# 	 subplot_id := id of the subplot where the parasite axis should be added
# 	 dist := distance (in terms of figure ratio) to keep with the adjacent axis
# 	"""
# 	# Retrieve the required parameters and set default values
# 	assert isinstance(side, str) and re.search('(?i)left|right|top|bottom', side), f'Invalid side \'{side}\''
# 	side = side.lower()
# 	# orient_id determines if the multiplot is in left/right mode of bottom/top mode
# 	orient_id = int(side in ('bottom', 'top'))
# 	side_id = int(side in ('right', 'top'))
	
# 	subplot_id = int(kwargs.pop('subplot_id', 0))
# 	# TODO: Figure out a way to make the distances between axes less figsize dependent
# 	dist = abs(kwargs.pop('dist', 0.01))
# 	debug = abs(kwargs.pop('debug', False)) # DEBUG

# 	# Bbox objects return the coordinates of the bottom-left and top-right points
# 	# Position of the plot boxes limits (non-dimensionnal by full figure): Axes.get_position()
# 	# Figure size (pixels): Figure.get_size_inches()*Figure.dpi
# 	# Get bbox around an element (figure pixel coords): Element.get_tightbbox(fig.canvas.get_renderer())

# 	# Find the host axes
# 	hosts, orig_pos = [], []
# 	for ax in fig.axes:
# 		ax_pos = ax.get_position()
# 		if len(hosts) == 0:
# 			hosts.append(ax)
# 		else:
# 			for h in hosts:
# 				hosts_pos = h.get_position()
# 				if all(ax_pos.p0 == hosts_pos.p0) and all(ax_pos.p1 == hosts_pos.p1):
# 					break
# 			hosts.append(ax)
# 		orig_pos.append(ax_pos)
# 	assert subplot_id <= len(hosts)-1, f'subplot_id ({subplot_id}) should be in the range [0, {len(hosts)-1}]'
# 	host = hosts[subplot_id]

# 	# Get the current box size (ratio of full figure) and figure size (pixels)
# 	box = host.get_position()
# 	figsize = (fig.get_size_inches()*fig.dpi)[('left','bottom').index(('left', 'bottom')[orient_id])]

# 	# Get a list of all axes on the desired subplot, and separate the two opposite sides of the axes
# 	# If we add a plot to the right, then only left and right positions will need to be tweaked.
# 	# The offset's units are [ratio_of_full_figure]
# 	# axes: { side1:{'ax':[ax1, ...], 'offset':[ax1_offset, ...], 'tightbbox':[ax1_tightbbox, ...]}, side2:{...} }
# 	axes = {('left', 'bottom')[orient_id]:{'ax':[], 'offset':[], 'tightbbox':[]}, ('right', 'top')[orient_id]:{'ax':[], 'offset':[], 'tightbbox':[]}}
# 	for ax in fig.axes:
# 		if all(host.get_position().p0 == ax.get_position().p0) and all(host.get_position().p1 == ax.get_position().p1):
# 			# Executes ax.yaxis... or ax.xaxis... depending on the side provided, to get the side of the ticks
# 			ax_side = getattr(ax, ('yaxis', 'xaxis')[orient_id]).get_ticks_position()
# 			# Save some data to axes
# 			axes[ax_side]['ax'].append(ax)
# 			# The top and right offsets have been substracted 1 for easier calculations, don't forget to add it later
# 			ax_position = ax.spines[ax_side].get_position()
# 			if ax_side in ('top', 'right') and ax_position[0] != 'outward':
# 				axes[ax_side]['offset'].append((ax_position[1]-1)*box.bounds[2+orient_id])
# 			else:
# 				axes[ax_side]['offset'].append(ax_position[1]*box.bounds[2+orient_id])
# 			axes[ax_side]['tightbbox'].append(getattr(ax, ('yaxis', 'xaxis')[orient_id]).get_tightbbox(fig.canvas.get_renderer()))

# 	# Sort the axes from left to right / bottom to top
# 	for s in axes:
# 		index_list = sorted(range(len(axes[s]['offset'])), key=axes[s]['offset'].__getitem__)
# 		for k in axes[s]:
# 			axes[s][k] = [axes[s][k][i] for i in index_list]
	
# 	# Fix a bug where twinx and twiny will be drawn on the "default" axes instead of the actual host
# 	fig.subplots_adjust()
		
# 	# Create a parasite Axes on the desired side
# 	# The following line chooses between twinx or twiny depending on the side needed
# 	par_ax = getattr(host, ('twinx', 'twiny')[orient_id])()
# 	getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).set_label_position(side)
# 	getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).set_ticks_position(side)

# 	# Fix a bug where twinx and twiny will be drawn on the "default" axes instead of the actual host
# 	for i,h in enumerate(hosts):
# 		h.set_position(orig_pos[i])

# 	# Hide the unnecessary spines
# 	par_ax.set_frame_on(True)
# 	par_ax.patch.set_visible(False)
# 	for sp in par_ax.spines.values():
# 		sp.set_visible(False)
# 	par_ax.spines[side].set_visible(True)

# 	# Plot the data and color the yaxis
# 	par_plot, = par_ax.plot(*args, **kwargs)
# 	getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).label.set_color(par_plot.get_color())
# 	par_ax.spines[side].set_color(par_plot.get_color())
# 	par_ax.tick_params(axis=('y', 'x')[orient_id], colors=par_plot.get_color())
	
# 	# Add the newly created parasite Axes' data and position it to calculate the new position of the box
# 	index = (len(axes[side]['ax']) + (not side_id)) % (len(axes[side]['ax']) + 1)
# 	axes[side]['ax'].insert(index, par_ax)
# 	if len(axes[side]['offset']) == 0:
# 		# If no axis is present, the newly added axis will not be moved
# 		axes[side]['offset'].insert(index, 0)
# 	else:
# 		# Returns the furthest x or y coordinate (ratio of full figure) of the axis in the correct orientation
# 		a = getattr(axes[side]['tightbbox'][-side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])/figsize
# 		# Returns the closest box coordinate to the new axis in the correct orientation
# 		b = getattr(box, (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
# 		# Calculation breakdown:
# 		# (2*side_id-1): Put a (-) sign if the axis is added on the left/bottom
# 		# abs(a-b): Distance from the box of furthest bbox
# 		axes[side]['offset'].insert(index, (2*side_id-1) * (abs(a-b)+dist))
# 	# box.bounds[2+orient_id]: box.bounds returns (x0, y0, width, height)
# 	par_ax.spines[side].set_position(('axes', side_id + (axes[side]['offset'][-side_id])/box.bounds[2+orient_id]))
# 	axes[side]['tightbbox'].insert(index, getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).get_tightbbox(fig.canvas.get_renderer()))
	
# 	# Calculate the new box dimensions
# 	new_bounds = list(box.bounds)
# 	if len(axes[side]['ax']) >= 2:
# 		# When there are 2 or more axis on the multiplot side,
# 		# the extra isthe distance between the bboxes' outer edges
# 		a = getattr(axes[side]['tightbbox'][1-2*side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
# 		b = getattr(axes[side]['tightbbox'][-2*side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
# 		extra = (a-b)/figsize
# 	else:
# 		# When there is only 1 axis on the multiplot side, the extra is the
# 		# distance between the multiplot's bbox's outer edge and the host box edge 
# 		a = getattr(box, (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
# 		b = getattr(axes[side]['tightbbox'][-side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
# 		extra = abs(a-b/figsize)
# 	# Modify only the dimensions of the correct orientation
# 	new_bounds[orient_id] = box.bounds[orient_id] + (not side_id)*extra
# 	new_bounds[2+orient_id] = new_bounds[2+orient_id] - extra
# 	# Set the new box dimensions to all axes
# 	host.set_position(new_bounds)

# 	# Reposition all axes (their position is defined as a ratio of the box size, but we just changed the box size!)
# 	for i,s in enumerate(axes):
# 		for j,ax in enumerate(axes[s]['ax']):
# 			ax.spines[s].set_position(('axes', i + (axes[s]['offset'][j])/new_bounds[2+orient_id]))
		
# 	return par_ax, par_plot