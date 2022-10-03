import cv2
import sys
import numpy
import random

# Helper "struct"
class FrameInfo():
    def __init__(self):
        self.Width:int = 0
        self.Height:int = 0
        self.FPS:float = 0

# Helper Functions
def GetArgs():
    return sys.argv[1:]
def CheckArgs(Args:list):
    if (len(Args) < 2):
        return False
    else:
        return True
def PrintHelp():
    print("Usage: python3 RainbowVision.py [input file.extension] [output file.extension] (Optional: Amount)")
    print("Example: python3 RainbowVision.py Input.mp4 Output.mp4 50")
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

    VideoSize:tuple = (int(VideoProperties.Width), int(VideoProperties.Height))
    Log(f"Video Output Resolution Will Be {VideoSize}")

    Log("Setting Up VideoWriter Instance")
    Fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    Writer = cv2.VideoWriter(Path, Fourcc, 30.0, VideoSize)
    Log("Setup VideoWriter Instance")

    Log("Writing Frames")
    NumberFrames:int = len(Frames)
    for FrameIndex in range(NumberFrames):
        Frame = Frames[FrameIndex]

        Writer.write(Frame)
        Log(f"Wrote Frame [{FrameIndex+1}/{NumberFrames}] ({round((FrameIndex+1)*100/NumberFrames)}%)")
    Log("Done Writing Frames")

    Log("Releasing VideoWriter")
    Writer.release()

def sp_noise(image,prob):
    '''
    Add salt and pepper noise to image
    prob: Probability of the noise
    '''
    output = numpy.zeros(image.shape,numpy.uint8)
    thres = 1 - prob 
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            rdn = random.random()
            if rdn < prob:
                output[i][j] = 0
            elif rdn > thres:
                output[i][j] = 255
            else:
                output[i][j] = image[i][j]
    return output

# Main Processing Function
def ProcessFrames(Frames:list, Arguments:list):

    # Check If Arguments Are Valid
    Log("Chekcing Arguments For Validity")
    Amount:int = 50
    if (len(Arguments) >= 3):
        Amount = int(Arguments[2])

    # Process Frames
    Log("Processing Frames")
    NumberFrames:int = len(Frames)
    for FrameIndex in range(len(Frames)):
        Frame = Frames[FrameIndex]

        Frame = Frame / Amount
        Frame = Frame * Amount

        Frame = sp_noise(Frame, 0.01*Amount)

        Frames[FrameIndex] = Frame
        Log(f"Processed Frame [{FrameIndex+1}/{NumberFrames}] ({round((FrameIndex+1)*100/NumberFrames)}%)")
    Log("Done Processing Frames")
    return Frames

# Main Function
def Main():

    # Get Arguments From The Terminal
    Arguments:list = GetArgs()
    if (not CheckArgs(Arguments)):
        PrintHelp()
        exit()

    # Load The Frames, Process, Write
    Frames, VideoInfo = LoadFrames(Arguments[0])
    Frames = ProcessFrames(Frames, Arguments)
    WriteFrames(Arguments[1], Frames, VideoInfo)

# If This Is The Main File, Run
if __name__ == "__main__":
    Main()
