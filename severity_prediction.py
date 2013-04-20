import argparse

parser = argparse.ArgumentParser()
parser.add_argument("cap_report", help="CAP report of storm",
                    type=str)
parser.add_argument("-d", "--debug", help="Show debug information", action="store_true")
args = parser.parse_args()

f = None
try:
    f = open(args.cap_report, 'r')
except IOError: # If file doesn't exist
    print 'Error opening', args.cap_report


# Parse CAP
# Extract Features
# Run through models
# Run predicted values through the classifer
# Output severity