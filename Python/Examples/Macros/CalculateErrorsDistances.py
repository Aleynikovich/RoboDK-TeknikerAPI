# This macro shows an example to implement the validation of distance errors after robot calibration.
# Update CSV_FILE variable to the appropriate CSV file with the measurement data.
# The measurements must be taken using a laser tracker such as an API laser tracker (point measurements).
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# Start RoboDK API
RDK = Robolink()

# Select the robot
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Use the CSV file exported after validation measurements are completed
CSV_VILE = 'Measurements Validation.csv'
csvdata = LoadList(RDK.getParam('PATH_OPENSTATION') + '/' + CSV_VILE)

# Iterate between consecutive points and check distances
print('p1\tp2\terror nominal (mm)\terror accurate (mm)')
num_points = len(csvdata)-1

# Faster calculation (do not render every time)
RDK.Render(False)

# Iterate:
for i in range(1,num_points):
    # Retrieve the robot Joints for point i
    ji = csvdata[i][0:6]
    
    # Retrieve the measured point i, measured by the tracker
    pi_ref = csvdata[i][6:9]

    # Retrieve the TCP for point i
    tcp_i = csvdata[1][9:12]

    # Calculate position of the TCP using nominal kinematics (pi_nom)
    robot.setAccuracyActive(False)
    pi_nom = robot.SolveFK(ji)*tcp_i

    # Calculate TCP using accurate kinematics (pi_acc)
    robot.setAccuracyActive(True)
    pi_acc = robot.SolveFK(ji)*tcp_i

    for j in range(i+1, i+2):#,numdata+1):

        # Same calculation for point j
        jj = csvdata[j][0:6]
        pj_ref = csvdata[j][6:9]
        tcp_j = csvdata[j][9:12]            
        robot.setAccuracyActive(False)
        pj_nom = robot.SolveFK(jj)*tcp_j
        robot.setAccuracyActive(True)
        pj_acc = robot.SolveFK(jj)*tcp_j

        # Calculate the distances seen by the tracker, by the nominal kinematics and by the accurate kinematics:
        dist_ref = distance(pi_ref, pj_ref)
        dist_nom = distance(pi_nom, pj_nom)
        dist_acc = distance(pi_acc, pj_acc)

        # Calculate the robot errors compared to the tracker errors
        error_nom = abs(dist_nom - dist_ref)
        error_acc = abs(dist_acc - dist_ref)

        # Display the data
        print('%i\t%i\t%.3f\t%.3f' % (i,j,error_nom, error_acc))
  
        
