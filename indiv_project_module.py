import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import numpy as np
from time import sleep


def create_region(width,length):    
    '''
    Create a rectangular network grid given a width and length.
    
    :param: width
    :type: int
    :param: length
    :type: int
    '''
    
    assert isinstance(width,int)
    assert isinstance(length,int)
    
    fig = plt.figure()
    region = fig.add_subplot(111)
    region.axis([0,width,0,length])
    region_array = np.zeros([length,width],dtype=int)
    
    return fig,region,region_array
    
    
def new_tower(width,length):
    '''
    Generate a new network tower within the network grid with a random location and coverage size.
    
    :param: width
    :type: int
    :param: length
    :type: int
    '''
    
    x_loc = random.randint(0,width-1) #x-position of tower
    y_loc = random.randint(0,length-1) #y-positin of tower
    
    tower_width = random.randint(1,width-x_loc)
    tower_length = random.randint(1,length-y_loc)
    
    return x_loc, y_loc, tower_width, tower_length

def tower_color():
    '''
    Randomly generate a color for the coverage area.
    Used when plotting the coverage area onto the network grid
    '''
    color = []
    for i in range(3):
        rgb = random.randint(0,255)
        color.append(rgb)
        
    return '#%02x%02x%02x' % (color[0],color[1],color[2])

def plot_tower(fig,region,width,length):
    '''
    Plot the new tower onto the network grid, and generate a Numpy array of ones and zeros to represent
    the coverage area of the tower.
    
    :param: fig
    :type: Matplotlib figure
    :param: region
    :type: Matplotlib figure subplot
    :param: width
    :type: int
    :param: length
    :type: int
    '''
    
    x_loc,y_loc,tower_width,tower_length = new_tower(width,length)
    tower_array = np.zeros([length,width],dtype=int) #length = rows, width = columns  
    
    for i in range(y_loc,y_loc+tower_length):
        for j in range(x_loc,x_loc+tower_width):
            tower_array[i][j] = 1
        
    hex_color = tower_color()
    whole_patch = patches.Rectangle([x_loc,y_loc],tower_width,tower_length,facecolor=hex_color,alpha=0.5)
    #region.add_patch(whole_patch)
            
    return tower_array, whole_patch, hex_color

def row_area(tower_row):
    '''
    Calculate a rectangular area of the trimmed coverage area represented by a row.
    Also returns the index and area dimensions.
    Each element of the row represents the length of the network at that width.
    The rectangular area of the row is calculated by multiplying the network length by the length of a sequence
    of non-zero elements.
    
    E.g. 
    Input: [1,2,2,1,0] , Output Area: 1*4 = 4 (First non-zeroelement multiplied by length of non-zero sequence)
    Input: [0,2,3,3,4], Output Area: 2*4 = 8
    
    :param: tower_row
    :type: list
            
    '''
    
    global area_xloc, area_length, area_width
    
    if set(tower_row) == ({0,1} or {1}) : #Area of first row of chunk, in case of split coverage
        rows = 0
        cols = 1
        max_area = 0
        for i in range(len(tower_row)):
            if (rows==0):
                rows = tower_row[i]
            elif (tower_row[i] == 0) or (i == len(tower_row)-1):
                if tower_row[i] == 1:
                    cols += 1
                area = rows*cols
                if area > max_area:
                    max_area = area
                    area_xloc = i-cols
                    if tower_row[i]>0:
                        area_xloc += 1
                    area_length = rows
                    area_width = cols
                    area = 0
                    cols = 1
                rows =0
            else:
                cols += 1
        return max_area, area_xloc, area_length, area_width
    else: #Area for subsequent rows
        rows = 0
        cols = 1
        max_area = 0
        for i in range(len(tower_row)): # 0 1 2 2 0
            if (rows==0):
                rows = tower_row[i]
            elif (tower_row[i]<rows) or (i == len(tower_row)-1):
                if tower_row[i] > 0:
                    cols += 1
                area = rows*cols
                if area > max_area:
                    max_area = area
                    area_xloc = i-cols
                    if tower_row[i]>0:
                        area_xloc += 1
                    area_length = rows
                    area_width = cols
                    area = 0
                    cols = 1
                rows =0
            else:
                cols += 1
        return max_area, area_xloc, area_length, area_width

def trim_tower(region_array,length,width,tower_array):   
    '''
    Trim off coverage area of the new tower that is already covered by existing network towers.
    Returns the largest rectangular area that is unique to the new tower, no coverage overlap.
    
    :param: region_array
    :type: NumPy Array
    :param: length
    :type: int
    :param: width:
    :type: int
    :param: tower_array
    :type: NumPy Array
    '''
    
    global max_area_xloc, max_area_yloc, max_area_length, max_area_width
    
    for i in range(length):
        for j in range(width):
            if tower_array[i][j]==region_array[i][j]: #Eliminate overlapping area from tower_array
                tower_array[i][j] = 0
    
    for i in range(1,length):
        for j in range(width):
            if tower_array[i][j] == 1:
                tower_array[i][j] += tower_array[i-1][j]

    max_area = 0
    for i in range(length):
        if all(j==0 for j in tower_array[i]):
            continue
        else:
            [area, area_xloc, area_length, area_width] = row_area(tower_array[i])
            if area > max_area:
                max_area = area
                max_area_xloc = area_xloc
                max_area_yloc = i
                max_area_length = area_length
                max_area_width = area_width
                
    return max_area_xloc, max_area_yloc, max_area_length, max_area_width

def plot_trimmed(fig,region,max_area_xloc,max_area_yloc,max_area_width,max_area_length,whole_patch,hex_color):
    '''
    Remove existing full-coverage patch of the new tower.
    Plot the trimmed coverage area onto the network grid.
    
    :param: fig
    :type: Matplotlib figure
    :param: region:
    type: Matplotlib figure subplot
    :param: max_area_xloc
    :type: int
    :param: max_area_yloc
    :type: int
    :param: max_area_width
    :type: int
    :param: max_area_length
    :type: int
    :param: whole_patch
    :type: Matplotlib patch
    :param: hex_color
    :type: str
    '''
    
    trimmed_patch = patches.Rectangle([max_area_xloc,max_area_yloc],max_area_width,max_area_length,facecolor=hex_color,alpha=0.5)
    #sleep(0.5)
    #whole_patch.remove()
    #sleep(0.2)
    region.add_patch(trimmed_patch)

def update_region(region_array,max_area_xloc,max_area_yloc,max_area_width,max_area_length):
    '''
    Update the network grid coverage array with the trimmed coverage area of the new tower
    
    :param: region_array
    :type: NumPy Array
    :param: max_area_xloc
    :type: int
    :param: max_area_yloc 
    :type: int
    :param: max_area_width
    :type: int
    :param: max_area_length
    :type: int
    '''
    
    for i in range(max_area_yloc,max_area_yloc+max_area_length):
        for j in range(max_area_xloc,max_area_xloc+max_area_width):
            region_array[i][j] = 1
    return region_array
    