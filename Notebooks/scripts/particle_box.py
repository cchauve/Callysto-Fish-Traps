
"""
Modified from:

Animation of Elastic collisions with Gravity

author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD
Please feel free to use and modify this, but keep the above information. Thanks!
"""
import numpy as np
from scipy.spatial.distance import pdist, squareform, cdist

import matplotlib.pyplot as plt
import scipy.integrate as integrate
import matplotlib.animation as animation
from IPython.display import HTML

import scripts
perimeter_raw = get_perimeter(1, 0.08, 0.2, 0.24, 0.0068)


class ParticleBox:
    """Orbits class
    
    init_state is an [N x 4] array, where N is the number of particles:
       [[x1, y1, vx1, vy1],
        [x2, y2, vx2, vy2],
        ...               ]

    bounds is the size of the box: [xmin, xmax, ymin, ymax]
    """
    def __init__(self,
                 init_state = [[1, 0, 0, -1],
                               [-0.5, 0.5, 0.5, 0.5],
                               [-0.5, -0.5, -0.5, 0.5]],
                 init_tide_state = [[-2,2],[2, 2]],
                 init_perimeter = [perimeter_raw[0], (perimeter_raw[1] * -1) + 0.2],
                 bounds = [-2, 2, -2, 2],
                 size = 0.04,
                 M = 0.05):
        self.init_state = np.asarray(init_state, dtype=float)
        self.init_tide_state = np.asarray(init_tide_state, dtype=float)
        self.init_perimeter = np.asarray(init_perimeter, dtype=float)
        self.M = M * np.ones(self.init_state.shape[0])
        self.size = size
        self.state = self.init_state.copy()
        self.tide_state = self.init_tide_state.copy()
        self.perimeter = self.init_perimeter.copy()
        self.time_elapsed = 0
        self.bounds = bounds
        

    def step(self, dt):
        """step once by dt seconds"""
        self.time_elapsed += dt
        
        # update positions
        self.state[:, :2] += dt * self.state[:, 2:]
        
        #check for fish hitting the trap
        dist_arr = cdist(self.state[:,:2], np.array(list(zip(self.perimeter[0], self.perimeter[1]))))
        hit_trap = (dist_arr.min(axis=1) < self.size)
        self.state[hit_trap, 2:] *= -1
        
        #print(dist_arr.shape)
        
        # check for crossing boundary
        crossed_x1 = (self.state[:, 0] < self.bounds[0] + self.size)
        crossed_x2 = (self.state[:, 0] > self.bounds[1] - self.size)
        crossed_y1 = (self.state[:, 1] < self.bounds[2] + self.size)
        crossed_y2 = (self.state[:, 1] > self.bounds[3] - self.size)

        self.state[crossed_x1, 0] = self.bounds[1] - self.size
        self.state[crossed_x2, 0] = self.bounds[0] + self.size

        self.state[crossed_y1, 1] = self.bounds[2] + self.size
        self.state[crossed_y2, 1] = self.bounds[3] - self.size

        #self.state[crossed_x1 | crossed_x2, 2] *= -1
        self.state[crossed_y1 | crossed_y2, 3] *= -1
        self.state[crossed_y1, 0] *= -1

        #moving boundary to show tidal movement
        if(self.bounds[3] > 0):
            self.bounds[3] = self.bounds[3] - (1/300)
            self.tide_state[1,:] = self.bounds[3]
            
            
def init():
    """initialize animation"""
    global box, rect
    particles.set_data([], [])
    tide.set_data([], [])
    perimeter.set_data([],[])
    rect.set_edgecolor('none')
    return particles, tide, perimeter, rect

def animate(i):
    """perform animation step"""
    global box, rect, dt, ax, fig
    box.step(dt)

    ms = int(fig.dpi * 2 * box.size * fig.get_figwidth()
             / np.diff(ax.get_xbound())[0])
    
    # update pieces of the animation
    rect.set_edgecolor('k')
    particles.set_data(box.state[:, 0], box.state[:, 1])
    particles.set_markersize(ms)
    tide.set_data(box.tide_state)
    perimeter.set_data(box.perimeter)
    return particles, tide, rect

if __name__ == "__main__":

    #------------------------------------------------------------
    # set up initial state
    np.random.seed(0)
    init_state = -0.5 + np.random.random((50, 4))
    init_state[:, :2] *= 3.9

    box = ParticleBox(init_state, size=0.04)
    dt = 1. / 30 # 30fps


    #------------------------------------------------------------
    # set up figure and animation
    fig = plt.figure()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                         xlim=(-3.2, 3.2), ylim=(-2.4, 2.4))
    ax.axis('off')

    # particles holds the locations of the particles
    particles, = ax.plot([], [], 'o', color='salmon', ms=6)

    # tide holds the tide level for each timestep
    tide, = ax.plot([], [], '-', color='blue', ms=2)

    # perimeter holds the trap
    perimeter, = ax.plot([],[], '-', color='grey', ms=2)

    # rect is the box edge
    rect = plt.Rectangle(box.bounds[::2],
                         box.bounds[1] - box.bounds[0],
                         box.bounds[3] - box.bounds[2],
                         ec='none', lw=2, fc='none')
    ax.add_patch(rect)



    # plt.rcParams["animation.html"] = "jshtml"

    ani = animation.FuncAnimation(fig, animate, frames=700,
                                  interval=10, blit=True, init_func=init)

    plt.close()


    # save the animation as an mp4.  This requires ffmpeg or mencoder to be
    # installed.  The extra_args ensure that the x264 codec is used, so that
    # the video can be embedded in html5.  You may need to adjust this for
    # your system: for more information, see
    # http://matplotlib.sourceforge.net/api/animation_api.html
    #ani.save('particle_box.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    #HTML(ani.to_html5_video())