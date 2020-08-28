# Built-in libraries
import re

# Pipy libraries
import matplotlib.pyplot as plt


class MultiPlot:
	"""
	Object that make it easy to generate plots with parasite axes. Valid parameters:
	 subplots := 
	 figsize := 
	 margins := [left, bottom, right, top], -1 for untouched
	 dist := distance between multiplot axes (in pixels)
	"""

	def __init__(self, subplots=1, figsize=None, margins=None, dist=10):
		# Parameters data type checks
		if figsize:
			assert isinstance(figsize, (list, tuple)) and len(figsize) == 2 and all([isinstance(n, (int,float)) for n in figsize]), '\'figsize\' parameter must be a list of 2 numbers'
		self.figure = plt.figure(figsize=figsize)
		self.figsize = self.figure.get_size_inches()*self.figure.dpi

		assert isinstance(dist, (int, float)), '\'dist\' parameter must be a number'
		self.dist = dist

		# self._subplots = [subplot_1, subplot_2, ...], where subplot_1 = [host, ax2, ax3, ...]
		self._subplots = []
		self._plots = []
		# self._sides = [subplot_1, subplot_2, ...], where subplot_1 = host_side
		self._sides = []
		
		if margins:
			assert isinstance(margins, (list, tuple)) and len(margins) == 4 and all([isinstance(n, (int,float)) for n in margins]), '\'margins\' parameter must be a list of 4 numbers'
		# 	self.margins = []
		# 	for i,m in enumerate(margins):
		# 		if m == -1:
		# 			self.margins.append(i>1)
		# 		else:
		# 			self.margins.append((i>1)*1+(i>1)*-1*m)
		# else:
		# 	self.margins = margins
			sides = ['left', 'bottom', 'right', 'top']
			adjustments = {}
			for i,m in enumerate(margins):
				if m != -1:
					if i > 1:
						adjustments[sides[i]] = 1 - m/self.figsize[i%2]
					else:
						adjustments[sides[i]] = m/self.figsize[i%2]
			self.subplots_adjust(**adjustments)
		
		if subplots == 1:
			self.subplot(111)
		elif subplots:
			assert isinstance(subplots, (list, tuple)), '\'subplots\' parameter must be a list'
			if len(subplots) == 2 and all([isinstance(s, (int,float)) for s in subplots]) and all(s < 111 for s in subplots):
				self.subplots(*subplots)
			else:
				for s in subplots:
					if isinstance(s, (int, float)):
						assert s >= 111, f'\'{s}\' is an invalid individual subplot definition (must be a 3 digit number or a 3 number list)'
						self.subplot(s)
					else:
						assert isinstance(s, (list, tuple)) and len(s) == 3, f'\'{s}\' is an invalid individual subplot definition (must be a 3 digit number or a 3 number list)'
						self.subplot(*s)

		self._color_cycle = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')
	
	def subplots_adjust(self, **kwargs):
		assert all([len(s) <= 1 for s in self._subplots]), 'subplots_adjust method must be called before creating any multiplot'
		# Executes Figure.subplots_adjust without messing with the multiplots
		# pos = [s[0].get_position() for s in self._subplots]
		# self.figure.tight_layout(rect=[0, 0.03, 1, 0.95])
		# plt.tight_layout()
		self.figure.subplots_adjust(**kwargs)
		# for i,s in enumerate(self._subplots):
		# 	s[0].set_position(pos[i])

	def subplot(self, *args, **kwargs):
		# Check for the number of axes before and after. If it has decreased, it means
		# a plot has been deleted, in which case we have no way to know which axes
		# are hosts and which are not hosts.
		plt.figure(self.figure.number)
		n_axes = len(self.figure.axes)
		self._subplots.append([plt.subplot(*args, **kwargs),])
		self._plots.append([])
		self._sides.append(['left', 'bottom'])
		assert len(self.figure.axes) == n_axes+1, 'Execution of the `subplot` method resulted in a deletion of a plot. All subplots must be generated without any deletion'
	
	def subplots(self, *args, **kwargs):
		# Check for the number of axes before and after. If it has decreased, it means
		# a plot has been deleted, in which case we have no way to know which axes
		# are hosts and which are not hosts.
		n_axes = len(self.figure.axes)
		axes = [[h,] for h in list(self.figure.subplots(*args, **kwargs).flatten())]
		self._subplots += axes
		self._plots += [[],]*len(axes)
		self._sides += [['left', 'bottom'],]*len(axes)
		assert len(self.figure.axes) == n_axes+args[0]*args[1], 'Execution of the `subplots` method resulted in a deletion of a plot. All subplots must be generated without any deletion'

	def plot(self, *args, subplot_id=0, main_side=None, side='left', parasite=True, colorize=True, dist=None, main_label=None, label=None, **kwargs):
		# Generate plot on the desired subplot_id, and create parasite axes if necessary
		assert isinstance(side, str) and re.search('(?i)left|right|top|bottom', side), f'Invalid side \'{side}\''
		if main_side: assert isinstance(main_side, str) and re.search('(?i)left|right|top|bottom', main_side), f'Invalid main_side \'{main_side}\''
		assert isinstance(subplot_id, (int, float)) and subplot_id < len(self._subplots), f'subplot_id ({subplot_id}) must be a number smaller than the number of subplots'
		# Cycle the color automatically
		n_lines = len(self._subplots[int(subplot_id)][0].get_lines())
		if not parasite or n_lines == 0:
			# Plot on the host plot if nothing is plotted on it
			plot, = self._subplots[int(subplot_id)][0].plot(*args, **kwargs)
			# Color the host axis, and color it back black if more lines are plotted on the host plot directly
			self._plot_format(self._subplots[int(subplot_id)][0], plot, main_side, side, colorize=(n_lines<=1), color=(None, '0')[n_lines==1], main_label=main_label, label=label)
			self._plots[subplot_id].append(plot)
			self._sides[subplot_id][side in ('bottom', 'top')] = side
			if main_side: self._sides[subplot_id][main_side in ('bottom', 'top')] = main_side
			# plt.tight_layout(rect=self.margins)
		else:
			if not (len(args) >= 3 and re.search('(?i)b|g|r|c|m|y|k|w', args[2])) and 'color' not in kwargs:
				kwargs['color'] = self._color_cycle[len(self._subplots[subplot_id])]
			# Multiplot
			ax, plot = self._multiplot(*args, subplot_id=subplot_id, side=side, dist=dist, label=label, **kwargs)
			self._subplots[subplot_id].append(ax)

	def overlay_plot(self, *args, subplot_id=0, ax_id=-1, **kwargs):
		assert isinstance(subplot_id, (int, float)) and subplot_id < len(self._subplots), f'subplot_id ({subplot_id}) must be a number smaller than the number of subplots ({len(self._subplots)})'
		assert isinstance(ax_id, (int, float)) and ax_id < len(self._subplots[subplot_id]), f'ax_id ({ax_id}) must be a number smaller than the number of axes in the subplot ({len(self._subplots[subplot_id])})'
		if 'color' not in kwargs:
			kwargs['color'] = self._plots[subplot_id][ax_id].get_color()
		self._subplots[int(subplot_id)][ax_id].plot(*args, **kwargs)

	def _plot_format(self, ax, plot, main_side=None, side='left', parasite=False, colorize=True, color=None, main_label=None, label=None):
		orient_id = int(side in ('bottom', 'top'))

		if main_side:
			main_orient_id = int(main_side in ('bottom', 'top'))
			assert main_orient_id != orient_id, f'main_side ({main_side}) must be in a different orientation than side ({side})'
			getattr(ax, ('yaxis', 'xaxis')[main_orient_id]).set_label_position(main_side)
			getattr(ax, ('yaxis', 'xaxis')[main_orient_id]).set_ticks_position(main_side)

		if main_label:
			getattr(ax, ('set_ylabel', 'set_xlabel')[not orient_id])(main_label)
		if label:
			getattr(ax, ('set_ylabel', 'set_xlabel')[orient_id])(label)

		getattr(ax, ('yaxis', 'xaxis')[orient_id]).set_label_position(side)
		getattr(ax, ('yaxis', 'xaxis')[orient_id]).set_ticks_position(side)

		if parasite:
			# Hide the unnecessary spines
			ax.set_frame_on(True)
			ax.patch.set_visible(False)
			for sp in ax.spines.values():
				sp.set_visible(False)
			ax.spines[side].set_visible(True)

		# Color the axis
		if colorize or color:
			if color is None: color = plot.get_color()
			getattr(ax, ('yaxis', 'xaxis')[orient_id]).label.set_color(color)
			# ax.spines[side].set_color(color)
			ax.tick_params(axis=('y', 'x')[orient_id], colors=color)
			if label:
				getattr(ax, ('yaxis', 'xaxis')[orient_id]).label.set_color(color)

	def _multiplot(self, *args, subplot_id=0, side='left', dist=None, label=None, debug=False, **kwargs):
		"""
		This function adds parasite axis to an already existing plot. If using a figure
		that has multiple subplots, all subplots must be created at the beginning of the figure generation.
		Valid parameters are:
		subplot_id := id of the subplot where the parasite axis should be added
		dist := distance (in terms of figure ratio) to keep with the adjacent axis
		"""
		# Retrieve the required parameters
		assert isinstance(subplot_id, (int, float)) and subplot_id < len(self._subplots), f'Invalid subplot_id ({subplot_id}), {len(self._subplots)} subplots were found'
		assert isinstance(side, str) and re.search('(?i)left|right|top|bottom', side), f'Invalid side \'{side}\''
		side = side.lower()
		if dist is None:
			dist = self.dist
		else:
			assert isinstance(dist, (int, float)), '\'dist\' parameter must be a number'

		# orient_id determines if the multiplot is in left/right mode of bottom/top mode
		orient_id = int(side in ('bottom', 'top'))
		side_id = int(side in ('right', 'top'))
		
		# Bbox objects return the coordinates of the bottom-left and top-right points
		# Position of the plot boxes limits (non-dimensionnal by full figure): Axes.get_position()
		# Figure size (pixels): Figure.get_size_inches()*Figure.dpi
		# Get bbox around an element (figure pixel coords): Element.get_tightbbox(fig.canvas.get_renderer())

		# Find the host axes
		# hosts, orig_pos = [], []
		# for ax in fig.axes:
		# 	ax_pos = ax.get_position()
		# 	if len(hosts) == 0:
		# 		hosts.append(ax)
		# 	else:
		# 		for h in hosts:
		# 			hosts_pos = h.get_position()
		# 			if all(ax_pos.p0 == hosts_pos.p0) and all(ax_pos.p1 == hosts_pos.p1):
		# 				break
		# 		hosts.append(ax)
		# 	orig_pos.append(ax_pos)
		# assert subplot_id <= len(hosts)-1, f'subplot_id ({subplot_id}) should be in the range [0, {len(hosts)-1}]'
		# host = hosts[subplot_id]

		# Get the current box size (ratio of full figure) and figure size (pixels)
		box = self._subplots[subplot_id][0].get_position()

		# Get a list of all axes on the desired subplot, and separate the two opposite sides of the axes
		# If we add a plot to the right, then only left and right positions will need to be tweaked.
		# The offset's units are [ratio_of_full_figure]
		# axes: { side1:{'ax':[ax1, ...], 'offset':[ax1_offset, ...], 'tightbbox':[ax1_tightbbox, ...]}, side2:{...} }
		axes = {('left', 'bottom')[orient_id]:{'ax':[], 'offset':[], 'tightbbox':[]}, ('right', 'top')[orient_id]:{'ax':[], 'offset':[], 'tightbbox':[]}}
		for ax in self._subplots[subplot_id]:
			# if all(host.get_position().p0 == ax.get_position().p0) and all(host.get_position().p1 == ax.get_position().p1):
			# Executes ax.yaxis... or ax.xaxis... depending on the side provided, to get the side of the ticks
			ax_side = getattr(ax, ('yaxis', 'xaxis')[orient_id]).get_ticks_position()
			# Save some data to axes
			axes[ax_side]['ax'].append(ax)
			# The top and right offsets have been substracted 1 for easier calculations, don't forget to add it later
			ax_position = ax.spines[ax_side].get_position()
			if ax_side in ('top', 'right') and ax_position[0] != 'outward':
				axes[ax_side]['offset'].append((ax_position[1]-1)*box.bounds[2+orient_id])
			else:
				axes[ax_side]['offset'].append(ax_position[1]*box.bounds[2+orient_id])
			axes[ax_side]['tightbbox'].append(getattr(ax, ('yaxis', 'xaxis')[orient_id]).get_tightbbox(self.figure.canvas.get_renderer()))

		# Sort the axes from left to right / bottom to top
		for s in axes:
			index_list = sorted(range(len(axes[s]['offset'])), key=axes[s]['offset'].__getitem__)
			for k in axes[s]:
				axes[s][k] = [axes[s][k][i] for i in index_list]
		
		# Fix a bug where twinx and twiny will be drawn on the "default" axes instead of the actual host
		orig_pos = [s[0].get_position() for s in self._subplots]
		self.figure.subplots_adjust()
			
		# Create a parasite Axes on the desired side
		# The following line chooses between twinx or twiny depending on the side needed
		par_ax = getattr(self._subplots[subplot_id][0], ('twinx', 'twiny')[orient_id])()
		par_plot, = par_ax.plot(*args, **kwargs)
		
		# Format the newly created parasite axis
		self._plot_format(par_ax, par_plot, side=side, parasite=True, label=label)
		if side_id:
			self._subplots[subplot_id][0].yaxis.set_label_position(self._sides[subplot_id][0])
			self._subplots[subplot_id][0].xaxis.set_label_position(self._sides[subplot_id][1])
			self._subplots[subplot_id][0].yaxis.set_ticks_position(self._sides[subplot_id][0])
			self._subplots[subplot_id][0].xaxis.set_ticks_position(self._sides[subplot_id][1])

		#  self._plot_format(self._subplots[subplot_id][0], 'dummmy', side=side, parasite=False, colorize=True, color=None, main_label=None, label=None):

		# getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).set_label_position(side)
		# getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).set_ticks_position(side)

		# # Fix a bug where twinx and twiny will be drawn on the "default" axes instead of the actual host
		for i,s in enumerate(self._subplots):
			s[0].set_position(orig_pos[i])

		# # Hide the unnecessary spines
		# par_ax.set_frame_on(True)
		# par_ax.patch.set_visible(False)
		# for sp in par_ax.spines.values():
		# 	sp.set_visible(False)
		# par_ax.spines[side].set_visible(True)

		# # Plot the data and color the yaxis
		# getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).label.set_color(par_plot.get_color())
		# par_ax.spines[side].set_color(par_plot.get_color())
		# par_ax.tick_params(axis=('y', 'x')[orient_id], colors=par_plot.get_color())
		
		# Add the newly created parasite Axes' data and position it to calculate the new position of the box
		index = (len(axes[side]['ax']) + (not side_id)) % (len(axes[side]['ax']) + 1)
		axes[side]['ax'].insert(index, par_ax)
		if len(axes[side]['offset']) == 0:
			# If no axis is present, the newly added axis will not be moved
			axes[side]['offset'].insert(index, 0)
		else:
			# Returns the furthest x or y coordinate (ratio of full figure) of the axis in the correct orientation
			a = getattr(axes[side]['tightbbox'][-side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])/self.figsize[orient_id]
			# Returns the closest box coordinate to the new axis in the correct orientation
			b = getattr(box, (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
			# Calculation breakdown:
			# (2*side_id-1): Put a (-) sign if the axis is added on the left/bottom
			# abs(a-b): Distance from the box of furthest bbox
			axes[side]['offset'].insert(index, (2*side_id-1) * (abs(a-b)+dist/self.figsize[orient_id]))
		# box.bounds[2+orient_id]: box.bounds returns (x0, y0, width, height)
		par_ax.spines[side].set_position(('axes', side_id + (axes[side]['offset'][-side_id])/box.bounds[2+orient_id]))
		axes[side]['tightbbox'].insert(index, getattr(par_ax, ('yaxis', 'xaxis')[orient_id]).get_tightbbox(self.figure.canvas.get_renderer()))
		
		# Calculate the new box dimensions
		new_bounds = list(box.bounds)
		if len(axes[side]['ax']) >= 2:
			# When there are 2 or more axis on the multiplot side,
			# the extra is the distance between the bboxes' outer edges
			a = getattr(axes[side]['tightbbox'][1-2*side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
			b = getattr(axes[side]['tightbbox'][-2*side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
			extra = (a-b)/self.figsize[orient_id]
		else:
			# When there is only 1 axis on the multiplot side, the extra is the
			# distance between the multiplot's bbox's outer edge and the host box edge 
			a = getattr(box, (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
			b = getattr(axes[side]['tightbbox'][-side_id], (('x0', 'x1'), ('y0', 'y1'))[orient_id][side_id])
			extra = abs(a-b/self.figsize[orient_id])
		# Modify only the dimensions of the correct orientation
		new_bounds[orient_id] = box.bounds[orient_id] + (not side_id)*extra
		new_bounds[2+orient_id] = new_bounds[2+orient_id] - extra
		
		# Set the new box dimensions to all axes
		self._subplots[subplot_id][0].set_position(new_bounds)

		# Reposition all axes (their position is defined as a ratio of the box size, but we just changed the box size!)
		for i,s in enumerate(axes):
			for j,ax in enumerate(axes[s]['ax']):
				ax.spines[s].set_position(('axes', i + (axes[s]['offset'][j])/new_bounds[2+orient_id]))
		
		self._plots[subplot_id].append(par_plot)
			
		return par_ax, par_plot