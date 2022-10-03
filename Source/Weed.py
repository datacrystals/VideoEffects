import cv2
import sys
import numpy

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
    print("Usage: python3 Weed.py [input file.extension] [output file.extension] [Number of frames between update] [blur amount] [blur iterations]")
    print("Example: python3 Weed.py in.mp4 out.mp4 8 0.03 10")
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

def Trip(Image, Amount):
    NewImage = cv2.blur(Image, (20,20))
    NewImage = NewImage % (255-Amount)
    NewImage *= (255-Amount)
    return NewImage

def BlitImage(Base, Image, Position:tuple):

    X,Y = Position
    Base[X:(X+Image.shape[0]), Y:(Y+Image.shape[1])] = Image
    return Base
def CropImage(Image, Position:tuple, Size:tuple):
    X,Y = Position
    W,H = Size
    return Image[X:X+W, Y:Y+H]
def RadialBlur(img, blur, iterations):
    w, h = img.shape[:2]

    center_x = h / 2
    center_y = w / 2

    growMapx = numpy.tile(numpy.arange(h) + ((numpy.arange(h) - center_x)*blur), (w, 1)).astype(numpy.float32)
    shrinkMapx = numpy.tile(numpy.arange(h) - ((numpy.arange(h) - center_x)*blur), (w, 1)).astype(numpy.float32)
    growMapy = numpy.tile(numpy.arange(w) + ((numpy.arange(w) - center_y)*blur), (h, 1)).transpose().astype(numpy.float32)
    shrinkMapy = numpy.tile(numpy.arange(w) - ((numpy.arange(w) - center_y)*blur), (h, 1)).transpose().astype(numpy.float32)

    for i in range(iterations):
        tmp1 = cv2.remap(img, growMapx, growMapy, cv2.INTER_LINEAR)
        tmp2 = cv2.remap(img, shrinkMapx, shrinkMapy, cv2.INTER_LINEAR)
        img = cv2.addWeighted(tmp1, 0.5, tmp2, 0.5, 0)
    
    return img

# Main Processing Function
def ProcessFrames(Frames:list, Arguments:list):

    # Check If Arguments Are Valid
    Log("Chekcing Arguments For Validity")
    NumFramesBetweenUpdates:int = 8
    BlurAmount:float = 0.04
    Iterations:int = 10
    if (len(Arguments) >= 3):
        NumFramesBetweenUpdates = int(Arguments[2])
    if (len(Arguments) >= 4):
        BlurAmount = float(Arguments[3])
    if (len(Arguments) >= 5):
        Iterations = int(Arguments[4])
        

    # Process Frames
    Log("Processing Frames")
    NumberFrames:int = len(Frames)

    Size = (int(Frames[0].shape[0] / 2), int(Frames[0].shape[1] / 2))
    Position = (int(Size[0]/2), int(Size[1]/2))

    FreezeFrame = CropImage(Frames[0], Position, Size)
    for FrameIndex in range(len(Frames)):
        Frame = Frames[FrameIndex]

        if (FrameIndex%NumFramesBetweenUpdates == 0):
            FreezeFrame = CropImage(Frame, Position, Size)
        Frame = BlitImage(Frame, FreezeFrame, Position)
        Frame = RadialBlur(Frame, BlurAmount, Iterations)

        Frames[FrameIndex] = numpy.uint8(Frame)
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
