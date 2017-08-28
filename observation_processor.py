def get_observation(self):
    bodies = ['head', 'pelvis', 'torso', 'toes_l', 'toes_r', 'talus_l', 'talus_r']

    pelvis_pos = [self.pelvis.getCoordinate(i).getValue(self.osim_model.state) for i in range(3)]
    pelvis_vel = [self.pelvis.getCoordinate(i).getSpeedValue(self.osim_model.state) for i in range(3)]

    jnts = ['hip_r','knee_r','ankle_r','hip_l','knee_l','ankle_l']
    joint_angles = [self.osim_model.get_joint(jnts[i]).getCoordinate().getValue(self.osim_model.state) for i in range(6)]
    joint_vel = [self.osim_model.get_joint(jnts[i]).getCoordinate().getSpeedValue(self.osim_model.state) for i in range(6)]

    mass_pos = [self.osim_model.model.calcMassCenterPosition(self.osim_model.state)[i] for i in range(2)]
    mass_vel = [self.osim_model.model.calcMassCenterVelocity(self.osim_model.state)[i] for i in range(2)]

    body_transforms = [[self.osim_model.get_body(body).getTransformInGround(self.osim_model.state).p()[i] for i in range(2)] for body in bodies]

    muscles = [ self.env_desc['muscles'][self.MUSCLES_PSOAS_L], self.env_desc['muscles'][self.MUSCLES_PSOAS_R] ]

    # see the next obstacle
    obstacle = self.next_obstacle()

#        feet = [opensim.HuntCrossleyForce.safeDownCast(self.osim_model.forceSet.get(j)) for j in range(20,22)]
    self.current_state = pelvis_pos + pelvis_vel + joint_angles + joint_vel + mass_pos + mass_vel + list(flatten(body_transforms)) + muscles + obstacle
    return self.current_state

'''
above was copied from 'osim-rl/osim/env/run.py'.

observation:
0 pelvis r
1 x
2 y

3 pelvis vr
4 vx
5 vy

6-11 hip_r .. ankle_l [joint angles]

12-17 hip_r .. ankle_l [joint velocity]

18-19 mass_pos xy
20-21 mass_vel xy

22-(22+7x2-1=35) bodypart_positions(x,y)

36-37 muscles psoas

38-40 obstacles

radius of heel and toe ball: 0.05

'''

def process_observation(observation):
    o = list(observation) # an array
    
    px = o[1]
    py = o[2]

    pvx = o[4]
    pvy = o[5]

    o = o + [o[22+i*2+1] for i in range(7)] # range: 42-54

    for i in range(7): # head pelvis torso, toes and taluses
        o[22+i*2+0] -= px
        o[22+i*2+1] -= py

    o[18] -= px # mass pos xy made relative
    o[19] -= py
    o[20] -= pvx
    o[21] -= pvy
    #if o[38]==100.0: o[38] = 0.0
    o[38]/=100.0
    o[39]/=5.0
    o[40]/=5.0

    o[1]=0 # abs value of pel x is not relevant


    return o

# expand observation from 41 to 41+14 = 55 dims
def generate_observation(new, old=None, step=0):
    # deal with old
    if old is None:
        old = list(new)

    # process new
    new_processed = process_observation(new)

    # calc vel
    bodypart_velocities = [(new_processed[i]-old[i])/0.01 for i in range(22,36)]

    # new_processed[1] = (999 - step)/1000

    # substitude old with new
    for i in range(41):
        old[i] = new_processed[i]

    # return processed
    new_processed = new_processed + bodypart_velocities

    # for i,n in enumerate(new_processed):
    #     print(i,n)

    return new_processed, old
