from tokenize import Number
import cv2
import sys

class FrameInfo():
    def __init__(self):
        self.Width:int = 0
        self.Height:int = 0
        self.FPS:float = 0

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

    Log("Getting Video Properties")
    FrameInfoInstance:FrameInfo = FrameInfo()
    FrameInfoInstance.FPS = Cap.get(cv2.CAP_PROP_FPS)
    FrameInfoInstance.Width = Cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    FrameInfoInstance.Height = Cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    Log("Loading Frames Into Memory For Processing")
    Frames = []
    CurrentFrame = 1

    while (Cap.isOpened()):
        Retention, Frame = Cap.read()

        if (Retention):
            Log(f"Loaded Frame [{CurrentFrame}/{NumberFrames}] ({round(CurrentFrame*100/NumberFrames)}%)")
            Frames.append(Frame)
            CurrentFrame += 1
        else:
            Log("Done, Releasing VideoStream")
            Cap.release()

    Log("Done Loading Frames")
    return Frames, FrameInfoInstance

def WriteFrames(Path:str, Frames:list, VideoProperties:FrameInfo):
    
    Log("Detecting VideoWriter Frame Properties")

    Log("Setting Up VideoWriter Instance")
    Fourcc = cv2.cv.CV_FOURCC(*'XVID')
    Writer = cv2.VideoWriter(Path, Fourcc, VideoProperties.FPS, (VideoProperties.Width, VideoProperties.Height))
    Log("Setup VideoWriter Instance")

    Log("Writing Frames")
    NumberFrames:int = len(Frames)
    for FrameIndex in range(NumberFrames):
        Frame = Frames[FrameIndex]

        Writer.write(Frame)
        Log(f"Wrote Frame [{FrameIndex}/{NumberFrames}] ({round(FrameIndex*100/NumberFrames)}%)")
    Log("Done Writing Frames")

    Log("Releasing VideoWriter")
    Writer.release()


def Main():

    Arguments:list = GetArgs()
    if (not CheckArgs(Arguments)):
        PrintHelp()
        exit()

    Frames, VideoInfo = LoadFrames(Arguments[0])
    




if __name__ == "__main__":
    Main()
