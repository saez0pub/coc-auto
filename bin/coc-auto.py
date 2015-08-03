#!/usr/bin/python2
# -*- coding: utf-8 -*-
version = 0.1

print "Clash of Clans Auto Tool for Genymotion (VirtualBox Android VM)"
print "Original source : https://gist.github.com/thuandt/e9cf284d7eb2d61dd99a"
print "version : "+str(version)

import os
import sys
import virtualbox
import subprocess
import cv2.cv as cv
from tesserwrap import Tesseract
import PIL.ImageOps as ImageOps
from time import sleep
from PIL import Image
import traceback
import time

# Genymotion Android VM name
sleepTime = 6
minK = 180
vbox = virtualbox.VirtualBox()
genymotion_vm_name = ""
scriptDir = os.path.dirname(os.path.realpath(__file__))
soundFile = scriptDir + "/../sound/Gun_Shot-Marvin-1140816320.mp3"
tessdataPrefix = scriptDir + "/../"

#COnstants Page mode
PSM_OSD_ONLY = 0
PSM_AUTO_OSD = 1
PSM_AUTO_ONLY = 2
PSM_AUTO = 3
PSM_SINGLE_COLUMN = 4
PSM_SINGLE_BLOCK_VERT_TEXT = 5
PSM_SINGLE_BLOCK = 6
PSM_SINGLE_LINE = 7
PSM_SINGLE_WORD = 8
PSM_CIRCLE_WORD = 9
PSM_SINGLE_CHAR = 10

def getTime():
  return time.strftime("%d/%m/%Y %H:%M:%S")

def getMenu():
 result = "Choose function?\n"
 result += "1. Keep Alive\n"
 result += "2. Auto Search\n"
 result += "3. wait full army then search an oponent\n"
 result += "4. Change Minimum K to stop ["+str(minK)+"]\n"
 result += "5. Change vm ["+genymotion_vm_name+"]\n"
 result += "6. Change sleepTime ["+str(sleepTime)+"]\n"
 result += "7. Quit\n"
 return result


def selectVM(genymotion_vm_name):
  global genymotion_session
  genymotion_vm = vbox.find_machine(genymotion_vm_name)
  genymotion_session = genymotion_vm.create_session()
  print "VM "+genymotion_vm_name

def click(x,y):
  global genymotion_session
  ts = getTime()
  genymotion_session.console.mouse.put_mouse_event_absolute(x,y,0,0,0)
  genymotion_session.console.mouse.put_mouse_event_absolute(x,y,0,0,1)
  genymotion_session.console.mouse.put_mouse_event_absolute(x,y,0,0,0)
  print "Clicking "+str(ts)+" : " + str(x)+","+str(y)
  #wait show fadein
  sleep(1)
  
def keep_alive():
    while True:
        print "Keepalive"
        click(400,230)
        sleep(60)

def takeScreenShot(imgTag):
  destImg = "/tmp/"+genymotion_vm_name+"-"+imgTag+".png"
  # processing
  subprocess.call("adb shell screencap -p /sdcard/screen.png", shell=True)
  subprocess.call("adb pull /sdcard/screen.png '"+destImg+"'", shell=True)
  print "ScreenShot saved as "+destImg
  return destImg

def cropImage(sourceImg,tagDest,*box):
  destOcrImg = "/tmp/"+genymotion_vm_name+"-"+tagDest+".png"
  im = Image.open(sourceImg)
  ocrImg = im.crop(box).convert('L')
  ocrImg.save(destOcrImg, "png")
  return destOcrImg

def ocrImage(tagDest,tessdataPrefix,lang,charWhitelist,pageMode):
  destOcrImg = "/tmp/"+genymotion_vm_name+"-"+tagDest+".png"
  print "OCR : "+str(destOcrImg)
  #OCR Def
  tr = Tesseract(tessdataPrefix, lang)
  tr.set_variable("tessedit_char_whitelist", charWhitelist)
  tr.set_page_seg_mode(pageMode)
  #OCR
  image = Image.open(destOcrImg)
  tr.set_image(image)
  return tr.get_utf8_text()

def auto_search():
  #wait the clouds to go
  sleep(sleepTime)
  #TODO : zoom out provide better OCR because of the trees
  ts = time.time()
  destImg = takeScreenShot("target")
  destLoot = cropImage(destImg,"loot",52, 67, 170, 130)
  img = Image.open(destLoot)
  img = ImageOps.invert(img)
  img.save(destLoot, "png")
  subprocess.call("convert "+destLoot+" -white-threshold 18% "+destLoot, shell=True)
  text = ocrImage("loot",tessdataPrefix, "coc","123456790",PSM_AUTO)
  print text
  print "toto"+scriptDir+'/../img/gold.png'+","+destImg
  print "gold at " + str(goldBox)
  elixirBox = findImg(scriptDir+'/../img/elixir.png',destImg)
  goldBox = (goldBox[2]+2,goldBox[1],goldBox[2]+120,goldBox[3])
  elixirBox = (elixirBox[2]+2,elixirBox[1],elixirBox[2]+120,elixirBox[3])
  destLootGold = cropImage(destImg,"gold",goldBox)
  destLootElixir = cropImage(destImg,"elixir",elixirBox)
  print  "gold single : " + ocrImage("gold",tessdataPrefix, "coc","123456790",PSM_SINGLE)
  print  "elixir single : " + ocrImage("elixir",tessdataPrefix, "coc","123456790",PSM_SINGLE)
  total_loot = text.splitlines()
  gold_loot, elixir_loot = total_loot[0:2]
  print "gold : \t"+gold_loot+"\nelixir :\t "+elixir_loot
  gold_expr = gold_loot.find(" ") == 3 and int(gold_loot.split(" ")[0]) >= minK
  elixir_expr = elixir_loot.find(" ") == 3 and int(elixir_loot.split(" ")[0]) >= minK

  if gold_expr or elixir_expr:
      print gold_loot
      print elixir_loot
      print destImg
      subprocess.call("play "+soundFile, shell=True)
      api.End()
      return True

  return False

def findImg(imgSearch,imgSrc):
  method = cv2.TM_CCOEFF_NORMED
  print "rtoto"
  img = cv2.imread(imgSrc,cv2.CV_LOAD_IMAGE_GRAYSCALE)
  print "ytoto"
  template = cv2.imread(imgSearch,cv2.CV_LOAD_IMAGE_GRAYSCALE)
  print "itoto"
  w, h = template.shape[0:2]
  res = cv2.matchTemplate(img,template,method)
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
  top_left = max_loc
  bottom_right = (top_left[0] + w, top_left[1] + h)
  return (top_left + bottom_right)

def searchInLoop():
  try:
      while auto_search() is False:
          # click search button
          print "Next"
          click(660,300)
          pass
  except:
      pass

def waitFullArmy():
  global genymotion_session
  while True:
    #click army icon
    click(40,290)
    ts = getTime()
    #get X/Y troops
    destImg = takeScreenShot("army")
    destLoot = cropImage(destImg,"troops",52, 67, 170, 130)
    text = ocrImage(destImg,"loot",None, "eng","0123456789/",PSM_SINGLE_LINE)
    #text = ocrImage(destImg,"troops","0123456789/",429,135,510,153)
    print "text : "+text
    text = text.splitlines()[0].replace(' ','')
    print text
    (numTroops, TotalTroops) = text.split('/')
    print ts + " "+str(numTroops)+" / "+str(TotalTroops)+" formed"
    #close army window => generate keepalive
    click(532,70)
    if numTroops == TotalTroops:
      break
    else:
      sleep(60)

if __name__ == "__main__":
    try:
        for vm in vbox.machines:
          print vm.name + " " + str(vm.state)
          if vm.state >= virtualbox.library.MachineState.running:
            genymotion_vm_name = vm.name
            break
        selectVM(genymotion_vm_name)
        while True:
            print getMenu()
            answer = raw_input("Your choice: ")
            if answer == "1":
                try:
                    keep_alive()
                except:
                    pass
            elif answer == "2":
          	print "Next"
          	click(660,300)
                searchInLoop()
            elif answer == "3":
                waitFullArmy()
                #Go to search oponent
                click(46,350)
                #find an oponent
                click(100,300)
                searchInLoop()
            elif answer == "4":
                minK = int(raw_input("Enter new minimum K to stop (old : "+str(minK)+"): "))
            elif answer == "5":
                print "VM List :"
                i=1
                for vm in vbox.machines:
                  if vm.state >= virtualbox.library.MachineState.running:
                    print str(i) + " " + vm.name
                    i=i+1
                answer = raw_input("Your choice: ")
                i=1
                for vm in vbox.machines:
                  if vm.state >= virtualbox.library.MachineState.running:
                    if str(i)==answer:
                      genymotion_vm_name=str(vm.name)
                      break
                    i=i+1
                selectVM(genymotion_vm_name)
            elif answer == "6":
                sleepTime = int(raw_input("Enter new sleepTime (old : "+str(sleepTime)+"): "))
            elif answer == "7":
                sys.exit(0)
    except KeyboardInterrupt:
      print "\nKeyboardInterrupt\nExit"
      sys.exit(0)
    except SystemExit:
      print "Exit"
      sys.exit(0)
    except:
        traceback.print_exc()
        print "Unexpected error:\n", sys.exc_info()[0]
        sys.exit(1)
