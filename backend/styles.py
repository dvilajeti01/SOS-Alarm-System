# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:59:39 2019

@author: VILAJETID
"""
import pandas
import re

def border(width=80):
        
    TOT_PIXEL = 1920
    LEFT_RATIO = .4
    RIGHT_RATIO = .6
        
    m_left = int((TOT_PIXEL * (1-width/float(100))) * LEFT_RATIO)
    m_right = int((TOT_PIXEL * (1-width/float(100))) * RIGHT_RATIO)
        
    return dict(selector="table",
                    props=[("border-collapse","collapse"),
                           ("width",str(width)+'%'),
                           ("margin-left",str(m_left)),
                           ("margin-right",str(m_right))])

def border_style(size="1px", density="solid", color="black",orientation="Left",pixels="2px"):
    return dict(selector="td, th",
                props=[("border","%s" % (str(size) + ' ' + str(density) + ' ' + str(color))),
                      ("text-align",str(orientation)),
                      ("padding",str(pixels))])
    
def header_color(back_color="#4286f4",text_color="white"):
    return dict(selector="th",props=[("background-color",str(back_color)),
                                                   ("color",str(text_color))])
    
def highlight_odd_rows(row):
    # Return array of booleans that apply a shaded color for odd rows in our DataFrame  
    return ['background-color: #F2F2F2' for cell in row]
            
def highlight_trigger_reading(row,color = 'darkorange'):
    #Apply style to the row to signal issue or alarm trigger
    style = 'background-color: %s' % color
    return [style for cell in row]

def draw_table(data,trigger_readings = [],headercolor = '#4286f4',border_collapse = True):
        """
        Function draws the table for a given sql query
        
        Parameters:
            trigger_readings: dict, A dictionary that maps rows that triggered 
            an alarm with a color specifying the alarm
        
        Return:
            html_string: str, Contains the html code which represents the table created as a string 
        """

        table = data.copy()
        
        styles = []
        
        if border_collapse:
            styles.append(border())
            
        styles.append(border_style())
        styles.append(header_color(headercolor))
        
        #Apply table styles (IMPORTANT: You must highlight odd rows first so you don't override the trigger reading row highlight)
        html_string = table.style.\
                            apply(highlight_odd_rows, subset = pandas.IndexSlice[1::2]).\
                            apply(highlight_trigger_reading, subset = pandas.IndexSlice[trigger_readings]).\
                            set_table_styles(styles).\
                            hide_index().\
                            render()

        #UGLY FIX TO THE TABLE PROBLEM
        html_string = re.sub("\s{4}#{1}[a-z|A-Z|0-9|_]{1,} table","table",html_string)
        
        print('\n'+html_string+'\n')
        
        return html_string
    