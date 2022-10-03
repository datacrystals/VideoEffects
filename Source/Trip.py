from tokenize import Number
import cv2
import sys

def GetArgs():
    return sys.argv[1:]
def CheckArgs(Args:list):
    if (len(Args) < 2):
        return False
    else:
        return True
def PrintHelp():
    print("Usage: Trip.py [input file.extension] [output file.extension]")
def Log(Message, Level=0):
    
    Code = ""
    if (Level==0):
        Code = "Info"
    elif (Level == 1):
        Code = "Warn"
    else:
        Code = "Crit"

    print(f"[{Code}] {Message}")
def LoadFrames(Path:str):
    Log(f"Loading Video Frames From Video {Path}")

    Log("Opening Capture To Video File")
    Cap = cv2.VideoCapture(Path)

    Log("Detecting Number Of Frames In Video File")
    NumberFrames:int = int(Cap.get(cv2.CAP_PROP_FRAME_COUNT))
    Log(f"Detected {NumberFrames} Frames In Video")

    Log("Loading Frames Into Memory For Processing")
    Frames = []
    CurrentFrame = 1

    while (Cap.isOpened()):
        Retention, Frame = Cap.read()

        if (Retention):
            Log(f"Loaded Frame [{CurrentFrame}/{NumberFrames}] ({CurrentFrame*100/NumberFrames}%)")
            Frames.append(Frame)
    
    Log("Done Loading Frames")



def Main():

    Arguments:list = GetArgs()
    if (not CheckArgs(Arguments)):
        PrintHelp()

    LoadFrames(Arguments[0])
    



if __name__ == "__main__":
    Main()
