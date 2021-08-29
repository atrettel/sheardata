#!/usr/bin/env python3

# Copyright (C) 2020-2021 Andrew Trettel
#
# SPDX-License-Identifier: MIT

# This file is a modified version of the Python module `grfstyl` created by
# Andrew Trettel.  See <https://github.com/atrettel/grfstyl/> for more details.

from cycler import cycler

# Units (follow TeX's lead)
mm_per_inch     = 25.4
points_per_inch = 72.27
points_per_mm   = points_per_inch / mm_per_inch

# Matplotlib mostly uses inches for length, but also uses points for line
# widths.
inch_unit   = 1.0
mm_unit     = 1.0 / mm_per_inch
points_unit = 1.0


# Aspect ratios
golden_ratio = 0.5*(5.0**0.5+1.0)
iso_ratio    = 2.0**0.5


# Page sizes
class PageSize:
    _name                = None
    _width               = None
    _height              = None
    _figure_aspect_ratio = None
    _figure_width_ratio  = None
    _dpi                 = None

    def dpi( self ):
        return self._dpi

    def name( self ):
        return self._name

    def height( self ):
        return self._height

    def width( self ):
        return self._width

    def shortest_length( self ):
        if ( self.height() > self.width() ):
            return self.width()
        else:
            return self.height()

    def longest_length( self ):
        if ( self.height() > self.width() ):
            return self.height()
        else:
            return self.width()

    def aspect_ratio( self ):
        return self.longest_length() / self.shortest_length()

    def figure_size( self, columns=1 ):
        return (
            self.figure_width(  columns=columns ),
            self.figure_height( columns=columns ),
        )

    def figure_width( self, columns=1 ):
        return self.width() * self._figure_width_ratio / float(columns)

    def figure_height( self, columns=1 ):
        return self.figure_width( columns=columns ) / self._figure_aspect_ratio

    # The maximum number of distinct "elements" that could be displayed in one
    # dimension.  This is a simple measure of the total amount of information
    # (the resolution) that can fit into any figure on a page of this size.
    def max_elements( self ):
        return int( self.dpi() * self.longest_length() )

    def __init__( self, name, width, height ):
        self._name                = name
        self._width               = width
        self._height              = height
        self._figure_aspect_ratio = golden_ratio
        self._figure_width_ratio  = 0.75
        self._dpi                 = 300.0

page_sizes           = {}
page_sizes["letter"] = PageSize( "letter",   8.5*inch_unit,  11.0*inch_unit )
page_sizes["a4"]     = PageSize( "a4",     210.0*  mm_unit, 297.0*  mm_unit )
page_sizes["beamer"] = PageSize( "beamer", 128.0*  mm_unit,  96.0*  mm_unit )

page_size = None


# Colors
black = [ 0.0 ] * 3
gray  = [ 0.5 ] * 3
white = [ 1.0 ] * 3
transparent_color = "None"

background_color = None
foreground_color = None
neutral_color    = None

axis_color = None
grid_color = None
plot_color = None
text_color = None


# Dimensions
no_line_width         = 0.0 * mm_unit
very_thin_line_width  = None
thin_line_width       = None
medium_line_width     = None
thick_line_width      = None
very_thick_line_width = None

axis_line_width   = None
grid_line_width   = None
plot_line_width   = None
marker_edge_width = None
error_bar_width   = None

marker_size        = None
error_bar_cap_size = None
major_tick_length  = None
minor_tick_length  = None
title_pad          = None
label_pad          = None


# Line styles
grid_line_style = "dotted"
plot_line_style = "solid"


# Functions
def aspect_ratio( xlim, ylim, goal_aspect_ratio=golden_ratio ):
    return ( xlim[1] - xlim[0] )   \
           /                       \
           ( goal_aspect_ratio     \
             *                     \
             ( ylim[1] - ylim[0] ) \
           )

def iso_line_width( level, default_width=0.35*mm_unit ):
    return round(                                       \
        ( default_width / mm_unit ) * iso_ratio**level, \
        2                                               \
    ) * points_per_mm

def label_axes( ax, x_label, y_label ):
    ax.set_xlabel(
        x_label,
        horizontalalignment="center",
        verticalalignment="top",
        rotation=0.0
    )
    ax.set_ylabel(
        y_label,
        horizontalalignment="right",
        verticalalignment="center",
        rotation=0.0
    )

def rc_custom_preamble( use_grid=True, tex_system="pdflatex", columns=1 ):
    pgf_preamble = [
        r"\usepackage{amsmath}",
        r"\usepackage{amsfonts}",
        r"\usepackage{amssymb}",
    ]
    return {
        "axes.edgecolor":        axis_color,
        "axes.facecolor":        background_color,
        "axes.grid":             use_grid,
        "axes.grid.axis":        "both",
        "axes.grid.which":       "both",
        "axes.labelcolor":       text_color,
        "axes.labelpad":         label_pad,
        "axes.linewidth":        axis_line_width,
        "axes.prop_cycle":       cycler( "color", [plot_color] ),
        "axes.spines.bottom":    True,
        "axes.spines.left":      True,
        "axes.spines.right":     False,
        "axes.spines.top":       False,
        "axes.titlepad":         title_pad,
        "axes.unicode_minus":    False,
        "errorbar.capsize":      error_bar_cap_size,
        "figure.dpi":            page_size.dpi(),
        "figure.edgecolor":      background_color,
        "figure.facecolor":      background_color,
        "figure.figsize":        page_size.figure_size( columns=columns ),
        "figure.frameon":        False,
        "grid.alpha":            1.0,
        "grid.color":            grid_color,
        "grid.linestyle":        grid_line_style,
        "grid.linewidth":        grid_line_width,
        "image.aspect":          "equal",
        "image.cmap":            "binary",
        "legend.borderaxespad":  0.5,
        "legend.borderpad":      0.8,
        "legend.columnspacing":  2.0,
        "legend.edgecolor":      axis_color,
        "legend.facecolor":      "inherit",
        "legend.fancybox":       False,
        "legend.framealpha":     1.0,
        "legend.frameon":        use_grid,
        "legend.handleheight":   0.7,
        "legend.handlelength":   2.0,
        "legend.handletextpad":  0.8,
        "legend.labelspacing":   0.5,
        "legend.loc":            "best",
        "legend.markerscale":    1.0,
        "legend.numpoints":      1,
        "legend.scatterpoints":  1,
        "legend.shadow":         "false",
        "lines.color":           plot_color,
        "lines.linestyle":       plot_line_style,
        "lines.linewidth":       plot_line_width,
        "lines.marker":          None,
        "lines.markeredgecolor": plot_color,
        "lines.markeredgewidth": marker_edge_width,
        "lines.markerfacecolor": background_color,
        "lines.markersize":      marker_size,
        "pgf.preamble":          pgf_preamble,
        "pgf.rcfonts":           False,
        "pgf.texsystem":         tex_system,
        "savefig.transparent":   True,
        "scatter.marker":        "o",
        "text.color":            text_color,
        "text.usetex":           False,
        "xtick.alignment":       "center",
        "xtick.bottom":          True,
        "xtick.color":           axis_color,
        "xtick.direction":       "out",
        "xtick.labelbottom":     True,
        "xtick.labeltop":        False,
        "xtick.major.pad":       major_tick_length,
        "xtick.major.size":      major_tick_length,
        "xtick.major.width":     axis_line_width,
        "xtick.minor.pad":       major_tick_length,
        "xtick.minor.size":      minor_tick_length,
        "xtick.minor.visible":   False,
        "xtick.minor.width":     axis_line_width,
        "xtick.top":             False,
        "ytick.alignment":       "center_baseline",
        "ytick.color":           axis_color,
        "ytick.direction":       "out",
        "ytick.labelleft":       True,
        "ytick.labelright":      False,
        "ytick.left":            True,
        "ytick.major.pad":       major_tick_length,
        "ytick.major.size":      major_tick_length,
        "ytick.major.width":     axis_line_width,
        "ytick.minor.pad":       major_tick_length,
        "ytick.minor.size":      minor_tick_length,
        "ytick.minor.visible":   False,
        "ytick.minor.width":     axis_line_width,
        "ytick.right":           False,
    }

def update_page_size( name, dark=False ):
    # Page sizes
    global page_size
    page_size = page_sizes[name]

    # Colors
    global background_color, foreground_color, neutral_color
    if ( dark ):
        background_color = black
        foreground_color = white
    else:
        background_color = white
        foreground_color = black
    neutral_color    = gray

    global axis_color, grid_color, plot_color, text_color
    axis_color = foreground_color
    grid_color = neutral_color
    plot_color = foreground_color
    text_color = foreground_color

    # Dimensions
    global very_thin_line_width, thin_line_width, medium_line_width, \
        thick_line_width, very_thick_line_width
    very_thin_line_width  = iso_line_width( -2 )
    thin_line_width       = iso_line_width( -1 )
    medium_line_width     = iso_line_width( +0 )
    thick_line_width      = iso_line_width( +1 )
    very_thick_line_width = iso_line_width( +2 )

    global axis_line_width, grid_line_width, plot_line_width, \
        marker_edge_width, error_bar_width
    axis_line_width   =    very_thin_line_width
    grid_line_width   =    very_thin_line_width
    plot_line_width   =       medium_line_width
    marker_edge_width =         thin_line_width
    error_bar_width   =       marker_edge_width

    global marker_size, error_bar_cap_size, major_tick_length, \
        minor_tick_length, title_pad, label_pad
    marker_size        = 4.0 * medium_line_width
    error_bar_cap_size = 2.0 * medium_line_width
    major_tick_length  = 4.0 * points_unit
    minor_tick_length  = 2.0 * points_unit
    title_pad          = 4.0 * points_unit
    label_pad          = 4.0 * points_unit

update_page_size("letter")
