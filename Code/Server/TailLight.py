import time
from pymaybe import maybe
from gpiozero import LED

class TailLight:
    
    def __init__(self, leftredpin, leftgreenpin, rightredpin, rightgreenpin):
        self.leftredpin = leftredpin
        self.leftgreenpin = leftgreenpin
        self.rightredpin = rightredpin
        self.rightgreenpin = rightgreenpin
        self.red = LED(leftredpin)
        self.green = LED(leftgreenpin)
        self.rightgreen = LED(rightgreenpin) if rightgreenpin != leftgreenpin else None
        self.rightred = LED(rightredpin) if rightredpin != leftredpin else None
        self.lgv = self.green.value
        self.rgv = self.rightgreen.value
        self.lrv = self.red.value
        self.rrv = self.rightred.value
        
    def bothred(self):
        self.green.off()
        maybe(self.rightgreen).off()
        self.red.on()
        maybe(self.rightred).on()    
    
    def bothgreen(self):
        self.red.off()
        maybe(self.rightred).off()
        self.green.on()
        maybe(self.rightgreen).on()    
    
    def saveValues(self):
        self.lgv = self.green.value
        self.rgv = self.rightgreen.value
        self.lrv = self.red.value
        self.rrv = self.rightred.value

    def loadValues(self):
        self.green.value = self.lgv 
        self.rightgreen.value = self.rgv
        self.red.value = self.lrv
        self.rightred.value = self.rrv 
                
    def rightblink(self):
        # Let's save the current stage to local values
        # Then blink the left red and leave the right red on
        # Maybe just blink 3 times then put things back how
        # they were?
        self.saveValues()
        self.bothred()
        maybe(self.rightred).blink(0.5, 0.5, 3, False)
        self.loadValues()

    def leftblink(self):
        self.saveValues()
        self.bothred()
        self.red.blink(0.5, 0.5, 3, False)
        self.loadValues()
    
    def flash(self):
        self.saveValues()
        for foo in range(1,3):
            self.bothred()
            time.sleep(0.5)
            self.off()
            time.sleep(0.5)
        self.loadValues()
        pass
    
    def off(self):
        self.green.off()
        self.red.off()
        maybe(self.rightgreen).off()
        maybe(self.rightred).off()
            
if __name__=='__main__':
    tl = TailLight(20,21,26,21)
    print("Red on")
    tl.bothred()
    time.sleep(3)
    print("Off")
    tl.off()
    time.sleep(2)
    print("Green on")
    tl.bothgreen()
    time.sleep(3)
    print("Left blink")
    tl.leftblink()
    print("Right blink")
    tl.rightblink()
    print("Flash")
    tl.flash()
    


        
    

