#  Shane Carty - 12713771
#  Orbital Prediction for Earth Observation

#  Methods to transform coordinates from ECI to ECEF


import math

# constants

MJD_J2000 = 51544.5    # Modif. Julian Date of J2000.0

GM_Earth = 398600.4415e+9 

R_Earth = 6378.1363E3 # Radius Earth [m] WGS-84

f_Earth  = 1.0/298.257223563 # Flattening WGS-84 

GM_Sun      = 1.32712438e+20    # [m^3/s^2] IAU 1976

GM_Moon     = GM_Earth/81.300587 # [m^3/s^2] DE200

Arcs  = 3600.0*180.0/math.pi     # Arcseconds per radian

Deg = 180.0 / math.pi          # Degrees per radian

Rad = math.pi / 180.0          # Radians per degree

AU = 149597870000.0      # Astronomical unit [m] IAU 1976

c_light = 299792458.0         # Speed of light  [m/s] IAU 1976

P_Sol = 4.560E-6          # [N/m^2] (~1367 W/m^2) IERS 96

JDminusMJD = + 2400000.5  # Difference in days between Julian to Modified Julian dates


    
     
def geodeticLLA( modPos,  mjd):
    daysSinceY2k = mjd - 51544.5

    ret = calculateGeodeticLLA(modPos, daysSinceY2k)
    #print('\ngeodeticLLA: ' + str(ret) + '\n')
    return ret

def calculateGeodeticLLA( r,  d):
    R_equ = R_Earth # Equator radius [m]
    f = f_Earth # Flattening

    eps_mach = 2.22E-16 # machine precision (?)

    eps     = 1.0e3*eps_mach   # Convergence criterion
    epsRequ = eps*R_equ
    e2      = f*(2.0-f)        # Square of eccentricity

    X = r[0]                   # Cartesian coordinates
    Y = r[1]
    Z = r[2]
    rho2 = X*X + Y*Y           # Square of distance from z-axis
    LLA = [None] * 3

    # Check validity of input data
    if norm(r)==0.0:
        LLA[1]=0.0
        LLA[0]=0.0
        LLA[2]=-R_Earth
        ret = LLA 
        return ret

    # Iteration
    dZ = 0
    dZ_new = 0
    SinPhi = 0
    ZdZ = 0
    Nh = 0
    N = 0

    dZ = e2*Z
    while True:
        ZdZ    =  Z + dZ
        Nh     =  math.sqrt( rho2 + ZdZ*ZdZ )
        SinPhi =  ZdZ / Nh                    # Sine of geodetic latitude
        N      =  R_equ / math.sqrt(1.0-e2*SinPhi*SinPhi)
        dZ_new =  N*e2*SinPhi
        if math.fabs(dZ-dZ_new) < epsRequ:
            break
        dZ = dZ_new

    # Longitude, latitude, altitude
    
    LLA[1] = math.atan2(Y, X)  # longitude,  lon
    LLA[0] = math.atan2( ZdZ, math.sqrt(rho2) ) # latitude, lat
    LLA[2] = Nh - N # altitute, h

    LLA[1] = LLA[1] -(280.4606 +360.9856473*d)*math.pi/180.0
    div = math.floor(LLA[1]/(2*math.pi))
    LLA[1] = LLA[1] - div*2*math.pi
    if LLA[1] > math.pi:
        LLA[1] = LLA[1]- 2.0*math.pi

    ret = LLA
    return ret 


def norm(a):
    c = 0.0
    for i in range(0, 3):
        c += a[i]*a[i]
    ret = math.sqrt(c)
    #print('\nnorm: ' + str(ret) + '\n')
    return ret
    

############################################################################################

     
def EquatorialEquinoxChange( mjdCurrentEquinox,   currentVec,  mjdNewEquinox):
    # first get precession matrix between the two dates
    prec =  PrecMatrix_Equ( (mjdCurrentEquinox-MJD_J2000)/36525, (mjdNewEquinox-MJD_J2000)/36525)
    ret = mult2(prec,currentVec) # transformed to new Equinox            
    return ret        
        

def EquatorialEquinoxFromJ2K(mjdNewEquinox, j2kPos):
    ret = EquatorialEquinoxChange(MJD_J2000, j2kPos, mjdNewEquinox)
    return ret        
     
def EquatorialEquinoxToJ2K( mjdCurrentEquinox,   currentPos):
    ret = EquatorialEquinoxChange(mjdCurrentEquinox, currentPos, MJD_J2000)
    return ret    
      

# helper method
def twoDList(list1):
    return isinstance(list1[0], list)
     
def PrecMatrix_Equ( T1,  T2):
    dT = T2-T1

    zeta = 0
    z = 0
    theta = 0
    
    zeta  =  ( (2306.2181+(1.39656-0.000139*T1)*T1)+((0.30188-0.000344*T1)+0.017998*dT)*dT )*dT/Arcs
    z     =  zeta + ( (0.79280+0.000411*T1)+0.000205*dT)*dT*dT/Arcs
    theta =  ( (2004.3109-(0.85330+0.000217*T1)*T1)-((0.42665+0.000217*T1)+0.041833*dT)*dT )*dT/Arcs 

    a = R_z(-z);
    b = R_y(theta);
    c = R_z(-zeta);

    ret =  mult1(mult1(a, b), c)
    return ret            

     
def mult1(a, b): 
    c = []
    c.append([None] * 3)
    c.append([None] * 3) 
    c.append([None] * 3) 
    for i in range(0,3): # row
        for j in range(0, 3): # col
            c[i][j] = 0.0
            for k in range(0, 3):
                c[i][j] += a[i][k] * b[k][j]

    ret = c 
    return ret    

def mult2( a,  b):
    c = [None] * 3
    for i in range(0,3): # row
        c[i] = 0.0
        for k in range(0, 3):
            c[i] += a[i][k] * b[k]
    ret = c
    return ret       

     
def R_x( Angle):
    C = math.cos(Angle)
    S = math.sin(Angle)
    U = []
    U.append([None] * 3)
    U.append([None] * 3)
    U.append([None] * 3) 
    U[0][0] = 1.0
    U[0][1] = 0.0
    U[0][2] = 0.0
    U[1][0] = 0.0
    U[1][1] = +C
    U[1][2] = +S
    U[2][0] = 0.0
    U[2][1] = -S
    U[2][2] = +C
    ret = U
    return ret       
    
     
def R_y( Angle):
    C = math.cos(Angle)
    S = math.sin(Angle)
    U = []
    U.append([None] * 3)
    U.append([None] * 3) 
    U.append([None] * 3) 
    U[0][0] = +C
    U[0][1] = 0.0
    U[0][2] = -S
    U[1][0] = 0.0 
    U[1][1] = 1.0
    U[1][2] = 0.0
    U[2][0] = +S
    U[2][1] = 0.0
    U[2][2] = +C
    ret = U
    return ret      

     
def R_z(Angle):
    C = math.cos(Angle)
    S = math.sin(Angle)
    U = []
    U.append([None] * 3)
    U.append([None] * 3)
    U.append([None] * 3) 
    U[0][0] = +C
    U[0][1] = +S
    U[0][2] = 0.0
    U[1][0] = -S
    U[1][1] = +C
    U[1][2] = 0.0
    U[2][0] = 0.0
    U[2][1] = 0.0
    U[2][2] = 1.0
    ret = U
    return ret      
    


def getLLA(eciX, eciY, eciZ, mJulDate):

    j2kEciPos = [eciX, eciY, eciZ]
    # modified jultian date of j2000 (or current ECI equinox)
    mJulDateJ2k = MJD_J2000

    modPos = EquatorialEquinoxChange(mJulDateJ2k, j2kEciPos, mJulDate)

    # now calculate Lat,Long,Alt - must use Mean of Date (MOD) Position
    result = geodeticLLA(modPos, mJulDate)
    return [result[0]*180.0/math.pi, result[1]*180.0/math.pi, result[2]] # current lat/long/altitude




