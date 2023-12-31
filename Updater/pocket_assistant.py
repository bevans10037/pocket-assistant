from os import remove, listdir, mkdir, system, rename, chdir
from os.path import isfile, exists, isdir
from shutil import rmtree, copytree, copy, move, SameFileError
from PIL import Image
import json
import sys

#If you are reading this code then I'm sorry in advance
#My only defense is that I think it works

class OpenJSON:
    def __init__(self,filename,encodeAsUTF8 = False,dictionary = False):
        self.filename = filename
        self.isUTF8 = encodeAsUTF8
        if dictionary:
            self.dictionary = dictionary
        else:
            if self.isUTF8:
                fileToRead = open(self.filename,"r",encoding="utf8")
            else:
                fileToRead = open(self.filename,"r")
            readFile = fileToRead.read()
            self.dictionary = json.loads(readFile)
            fileToRead.close()
    def save(self):
        if self.isUTF8:
            f = open(self.filename,"w",encoding="utf8")
        else:
            f = open(self.filename,"w")
        f.write(json.dumps(self.dictionary, sort_keys=True, indent=4))
        f.close()

def mergetree(i,o):
    if not isdir(o):
        mkdir(o)
    for x in listdir(i):
        if isfile(i + "/" + x):
            try:
                copy(i + "/" + x, o + "/" + x)
            except SameFileError:
                pass
        elif isdir(i + "/" + x):
            mergetree(i + "/" + x, o + "/" + x)

def yes_no_input(message):
    while True:
        userInput = input(message + "\n")
        if userInput.lower() == "y":
            return True
            break
        elif userInput.lower() == "n":
            return False
            break
        else:
            print("Invalid input.")

def make_image(gameName):
    if not exists("../Updater/_assistantimages/" + gameName + ".bin"): #check we haven't already made it
        imageFile = ""
        while imageFile == "": #locate image file
            for z in listdir("../Updater/_assistantimages/"):
                if z[0:len(gameName)+1] == gameName + ".":
                    imageFile = z
            if imageFile == "":
                input("Please place an image for the game " + gameName + " in Updater/_assistantimages/! Press enter when complete.")
        platformImage = Image.open("../Updater/_assistantimages/" + imageFile).convert("RGBA") #open with alpha channel (since it's likely to be a logo)
        platImWidth, platImHeight = platformImage.size
        if platImWidth == 521 and platImHeight == 165: #exactly right
            newWidth, newHeight = platImWidth, platImHeight
            x1, y1 = 0, 0
        elif platImWidth < 500 and platImHeight < 145: #too small - then integer scale up. Otherwise, pixel perfect logos might look blurry. Also we pick 521 and 165 to leave at least a bit of a border
            integerscalefactor = min(500 // platImWidth, 145 // platImHeight)
            platformImage = platformImage.resize((platImWidth*integerscalefactor,platImHeight*integerscalefactor),resample=Image.NEAREST)
            platImWidth, platImHeight = platformImage.size
            newWidth,newHeight = 521, 165 # basically means when we resize it later, nothing happens (since we don't want scaling on these)
            x1, y1 = round(newWidth/2 - platImWidth/2), round(newHeight/2 - platImHeight/2)
        else: #too big - scale down. Unlikely to be a pixel perfect logo in this case anyway.
            if platImWidth/platImHeight > 500/145: #too wide
                newWidth = platImWidth * 165 // 145
                newHeight = newWidth * 165 // 521
            elif platImWidth/platImHeight < 521/165: #too tall
                newHeight = platImHeight * 521 // 500
                newWidth = newHeight * 521 // 165
            x1, y1 = round(newWidth/2 - platImWidth/2), round(newHeight/2 - platImHeight/2)
        bg = Image.new('RGBA', (newWidth, newHeight), "WHITE")
        bg.paste(platformImage, (x1,y1), mask=platformImage) #platformImage now has the white background bg underneath it
        platformImage = bg.resize((521,165))
        platformImage = platformImage.convert("L") #monochrome
        platformImage.save("../Updater/_assistantimages/Analogue-Pocket-Image-Process-master/" + gameName + '.png')
        chdir("_assistantimages/Analogue-Pocket-Image-Process-master")
        system("npm run create \"" + gameName + ".png\" \"" + gameName + ".bin") #process the image
        system("title Pocket Assistant! :)") #because it changes the title
        chdir("../../") #come back to original folder
        move("../Updater/_assistantimages/Analogue-Pocket-Image-Process-master/" + gameName + ".bin","../Updater/_assistantimages/" + gameName + ".bin") #store in _assistantimages
        remove("../Updater/_assistantimages/Analogue-Pocket-Image-Process-master/" + gameName + ".png")

def make_platform_data(gameName, category = ""):
    #Pretty simple - just for getting new platform data from a user
    print("The " + gameName + " core needs new platform data!")
    platformDict = {}
    platformDict["name"] = input("Please give the real name of the core. ")
    if category == "":
        platformDict["category"] = input("Please give the real category of the core. ")
    else:
        platformDict["category"] = category
    while True:
        year = input("Please give the real year of release for the core. ")
        try:
            platformDict["year"] = int(year)
            break
        except ValueError:
            print("Invalid input.")
    platformDict["manufacturer"] = input("Please give the real manufacturer of the core. ")
    print("\n")
    return platformDict
    
def dont_download_assets(coreName):
    #Open the pocket_updater settings, and tell it to skip downloading assets for the given core
    if isfile("../pocket_updater_settings.json"):
        a = open("../pocket_updater_settings.json","r")
        updaterSettings = OpenJSON("../pocket_updater_settings.json")
        updaterSettings.dictionary["coreSettings"][coreName] = {"skip":True,"download_assets":False,"platform_rename":False}
        updaterSettings.save()
        
def compare_core_release(core1,core2):
    # Compare the date_release field of two cores - true if core1 is newer, false otherwise
    core1JSON = OpenJSON("../Cores/" + core1 + "/core.json")
    core2JSON = OpenJSON("../Cores/" + core2 + "/core.json")
    if core1JSON.dictionary["core"]["metadata"]["date_release"] > core2JSON.dictionary["core"]["metadata"]["date_release"]:
        return True
    else:
        return False

def edit_list(listToEdit, listDescription, advice = ""):
    while True:
        system("cls")
        print("Editing list of " + listDescription + "...\n")
        for x in listToEdit:
            print("\t" + x)
        if advice != "":
            print("\n" + advice)
        userInput = input("\nPlease give us an entry. If it's not in the list, we'll add it. If it is in the list, we'll remove it. Or, leave the field blank and press Enter to return to the previous menu!\n")
        if userInput == "":
            return listToEdit
        elif userInput in listToEdit:
            listToEdit.remove(userInput)
        else:
            listToEdit.append(userInput)

def edit_dict(dictToEdit, dictDescription, inputPrompt1, inputPrompt2, advice = ""):
    while True:
        system("cls")
        print("Editing list of " + dictDescription + "...\n")
        for x in dictToEdit.keys():
            print("\t" + x + ", using " + dictToEdit[x])
        if advice != "":
            print("\n" + advice)
        userInput1 = input("\n" + inputPrompt1 + "\n")
        if userInput1 == "":
            return dictToEdit
        elif userInput1 in dictToEdit.keys():
            dictToEdit.pop(userInput1)
        else:
            userInput2 = input(inputPrompt2 + "\n")
            dictToEdit[userInput1] = userInput2



#FIRST TIME SETUP
def setup_data(dataToReplaceWith):
    global assistantData
    if not exists("assistant_data.json"):
        #First, inherit the base data, then ask the user if they want the program to do each of the things it can do!
        assistantData = OpenJSON("assistant_data.json", dictionary = dataToReplaceWith)

        assistantData.dictionary["programSettings"]["clean"] = yes_no_input("Would you like this program to clean your assets? That is, when you download or update a core that comes with JSON files, this will hide the JSONs you don't want automatically. (y/n)")
        if assistantData.dictionary["programSettings"]["clean"]:
            assistantData.dictionary["programSettings"]["clone"] = yes_no_input("Would you like this program to clone cores where necessary? That is, when you have a core with multiple JSON files, this will make copies of the core so each JSON has its own core. (y/n)")
            assistantData.dictionary["programSettings"]["autostart"] = yes_no_input("Would you like this program to autostart cores? That is, for all supported cores - which is most of them - if you only have one JSON file in the directory, this will make the core automatically load it. (y/n)")
        else: #Because these are dependent on data collected from the cleaning
            assistantData.dictionary["programSettings"]["clone"] = False
            assistantData.dictionary["programSettings"]["autostart"] = False
        assistantData.dictionary["programSettings"]["platforms"] = yes_no_input("Would you like this program to clean the platform JSONs for you? That is, when you download a core with an unusual category, this will prompt you for help putting it in the right place. (y/n)")
        assistantData.dictionary["programSettings"]["aspect"] = yes_no_input("Would you like this program to correct aspect ratios for you? This will integer scale all cores, except for any you tell us not to, and a few that we've already noticed don't play nice with it. (y/n)")
        assistantData.dictionary["programSettings"]["rename"] = yes_no_input("Would you like this program to rename platform data for you? This will link whichever cores you specify to whatever platform you like. (y/n)")
        assistantData.dictionary["programSettings"]["favourites"] = yes_no_input("Would you like this program to generate a \"favourites\" core category, with cloned cores that link to specific games? (y/n)")
        assistantData.dictionary["programSettings"]["altcores"] = yes_no_input("Would you like this program to make copies of cores to allow you to switch between presets on your device? (y/n)")
        
        assistantData.dictionary["favouriteData"]["categoryName"] = ""
        assistantData.save()

def scan_for_JSONs(folder, originalFolder=""):
    # scannedList is a list of all jsons in all subdirectories, folderList is a list of the subdirectories searched through
    if originalFolder == "":
        originalFolder = folder
    scannedList = []
    folderList = []
    for x in listdir(folder):
        if x[x.rfind("."):] == ".json":
            scannedList.append(x[0:x.rfind(".")])
        elif isdir(folder + "/" + x):
            subfolderData = scan_for_JSONs(folder + "/" + x, originalFolder=originalFolder)
            scannedList = scannedList + subfolderData[0]
            if subfolderData[0] != []:
                folderList = folderList + subfolderData[1] + [folder + "/" + x + "/"]
    if folder == originalFolder:
        for x in range(len(folderList)):
            folderList[x] = folderList[x][len(folder)+1:]
    return scannedList, folderList

#CLEAN ASSETS FOLDERS
def clean_assets():
    system("cls")
    
    if assistantData.dictionary["cleanData"]["versionList"] == {}: #So, this part of the program is being run for the first time
    
        # Prompt saying what's going to get deleted and redownloaded, check if they're ok with that, and if they aren't turn off the clean_assets bool from here
        if yes_no_input("Hello! We're detecting you're running the asset cleaning part of the program for the first time. To set up our database, we're now going to delete and redownload any core that has associated JSON files. You'll then have to pick which JSON files to keep, and what you want them to be called. This may take a while! Do you still want to continue? (y/n)"):
            
            # Delete all cores that are attached to JSON files + their asset folders
            for x in listdir("../Cores"):
                if isdir("../Cores/" + x):
                    coreJSON = OpenJSON("../Cores/" + x + "/core.json")
                    # (Check the assets folder for JSON files)
                    if isdir("../Assets/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + x):
                        foundJSONs = False
                        for y in listdir("../Assets/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + x):
                            if y[y.rfind("."):] == ".json":
                                remove("../Assets/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + x + "/" + y)
                                foundJSONs = True
                        if foundJSONs:
                            rmtree("../Cores/" + x)
                            if exists("../Presets/" + x):
                                rmtree("../Presets/" + x)
            
            # Download all cores again (and just update any in general) with pocket_updater.exe - also change the JSON file for that to make sure it skips assets
            input("If you don't want the updater to download assets (which I would recommend) please turn that off in the settings. When you press Enter, we'll automatically update all your missing cores.")
            system("pocket_updater.exe update -p ../")
            
            # This part only does anything in one scenario: this is the first time we have run the core since resetting assistant_data.json, and the user chose to preserve their data
            # I can't remember why I did this, but I guess it is important. Sorry!
            if "nextVersionList" in assistantData.dictionary["cleanData"].keys():
                assistantData.dictionary["cleanData"]["versionList"] = assistantData.dictionary["cleanData"]["nextVersionList"]
                assistantData.dictionary["cleanData"].pop("nextVersionList")
                
            # And then we're done! 
            
        else: #So - they've bailed and don't want to run the asset cleaning any more
            assistantData.dictionary["programSettings"]["clean"] = False
            assistantData.dictionary["programSettings"]["clone"] = False
            assistantData.dictionary["programSettings"]["autostart"] = False
            print("\nOkay! I've changed the program settings to not run the asset cleaning part.")
    
    directory = listdir("../Cores") #We keep this as a separate variable because we'll sometimes want to remove items from it
    if assistantData.dictionary["programSettings"]["clean"]:
        #We check again now in case someone has run it for the first time, then decided they don't want to do it any more
        
        for x in directory:            
            #This part of the program is split into two parts:
            userPicksJSONs = False #This is the part where, if the core is new, or has been updated with new JSON files, we give the user all the JSON files in the directory, and they pick which ones they want.
            cleanCore = False      #This is the part where, if the core is new or has been updated at all (new JSON files or not), we hide all the JSON files a user hasn't previously said they want in a userPicksJSONs check, and rename all the ones they did want to whatever they told us then.
            
            preserveData = False   #This comes under userPicksJSONs - if it's an update, the user may want to keep what they wrote last time. This is where we store that decision
            newJsonList = {}       #This is where we would end up storing the user's input from userPicksJSONs
                
            if isdir("../Cores/" + x) and not x in assistantData.dictionary["cleanData"]["skip"] and not x[0:x.find(".")] in ["clones","faves"]:
                # So, it is a directory => a core, and it's not a clone core or a fave core
                system("cls")
                print("Cleaning assets...\n\t" + x)
                
                coreJSON = OpenJSON("../Cores/" + x + "/core.json")
                if not x in assistantData.dictionary["cleanData"]["versionList"].keys():
                    #Then this is a compately new core, and we have to add it to the versionlist - and ask the user if they want to add it to the jsonList
                    print("New core detected! Core name: " + x)
                    assistantData.dictionary["cleanData"]["versionList"][x] = coreJSON.dictionary["core"]["metadata"]["date_release"]
                    
                    if assistantData.dictionary["programSettings"]["clone"]: #If we're even cloning cores...
                        # We ask if we should add this to the "cloneSkip" list.
                        if yes_no_input("Would you like to create clone cores for this core? This means that every game remaining after cleaning the assets will get its own dummy version of the core, and appear separately in the core selection menu. We recommend you do this for arcade cores with only a few games attached. (y/n)"):
                            assistantData.dictionary["cloneData"]["skip"].append(x)
                    
                    #First time running for this core - so we want to do both parts of this function - both checking with the user and cleaning the jsons.
                    userPicksJSONs = True
                    cleanCore = True
                    
                elif coreJSON.dictionary["core"]["metadata"]["date_release"] > assistantData.dictionary["cleanData"]["versionList"][x]:
                    #On the other hand, this will mean a new update has been installed, so it's a mix of old (cleaned) stuff and all the new JSONs in there
                    
                    #First we update our records in versionList with the new date_release value.
                    assistantData.dictionary["cleanData"]["versionList"][x] = coreJSON.dictionary["core"]["metadata"]["date_release"]

                    #Check if this is a core with associated json files to clean
                    if x in assistantData.dictionary["cleanData"]["cores"].keys():
                        
                        #Delete the old stuff that's in the correct formatting - as long as it's not a case of the file already having the correct name anyway
                        rootFolderName = assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"]
                        for y in assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys():
                            if assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] != y and exists("../Assets/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json"):
                                remove("../Assets/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json")
                                if exists("../Presets/" + x + "/Input/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json"):
                                    remove("../Presets/" + x + "/Input/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json")
                                if exists("../Presets/" + x + "/Interact/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json"):
                                    remove("../Presets/" + x + "/Interact/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json")
                        
                        #Now check which JSON files are now there
                        JSONFiles = []
                        if isdir("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x): #if the possible subdirectory even exists
                            JSONFiles = scan_for_JSONs("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x)[0]

                        #We now see if there's a different number of json files to what we saw last time.
                        if assistantData.dictionary["cleanData"]["cores"][x]["expectedNewJSONs"] != len(JSONFiles):
                            #So now we need to update our records, and prompt the user to check if they want to keep these new json files
                            assistantData.dictionary["cleanData"]["cores"][x]["expectedNewJSONs"] = len(JSONFiles)
                            print("New update detected for core name: " + x + "\nWe have detected that new JSON files have been added to the directory for this core, which could mean for instance that new games have been added.")
                            while True:
                                userInput = input("Would you like to:\n\t1. ...rerun the setup process completely to add them?\n\t2. ...rerun the setup process but preserve the current data?\n\t3. ...do neither, and keep the current data as is?\n\t(1/2/3) ")
                                if userInput == "1":
                                    userPicksJSONs = True
                                    print("\nOkay! I will first give you the current data we have on the core.\n" + str(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"]))
                                    break
                                if userInput == "2":
                                    userPicksJSONs = True
                                    preserveData = True #The all-important difference to option 1
                                    print("\nOkay! I will first give you the current data we have on the core.\n" + str(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"]))
                                    break
                                elif userInput == "3":
                                    print("\n") #As if nothing happened
                                    break
                                else:
                                    print("Invalid input.")
                                    
                        #If there's more than 1 game (post-cleaning) attached to a core, then we may have cloned the core elsewhere. If so, we should now delete those cloned cores, as they're out of date.
                        #(The clone_cores function will then recreate those cores later!)
                        if len(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys()) > 1:
                            for y in range(len(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys())-1):
                                if not x in assistantData.dictionary["cloneData"]["skip"] and exists("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1)) and not x + str(y+1) in assistantData.dictionary["cleanData"]["cores"].keys():
                                    #so if the folder exists, and it isn't a core in its own right (see e.g. jtcps1 and jtcps15), AND we're even cloning that core to begin with...
                                    mergetree("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1) + "/common", "../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/common")
                                    rmtree("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1))
                                if exists("../Cores/clones." + x[x.find(".")+1:] + str(y+1)):
                                    rmtree("../Cores/clones." + x[x.find(".")+1:] + str(y+1))
                                if exists("../Presets/clones." + x[x.find(".")+1:] + str(y+1)):
                                    rmtree("../Presets/clones." + x[x.find(".")+1:] + str(y+1))
                        cleanCore = True
                
                #Now we get into the real thrust of the function - getting the info from the user
                if userPicksJSONs:
                    currentPlatform = coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] #We are assuming here that we won't have jsons over different platforms - but this hasn't happened yet to be fair
                    
                    if isdir("../Assets/" + currentPlatform + "/" + x): #So if it finds a folder with the name of the core...
                        #We need to get a list of all the JSONs attached to the core.
                        #(As we're here, we'll also get a list of all subdirectories containing JSONs, which will be useful later)
                        JSONData = scan_for_JSONs("../Assets/" + currentPlatform + "/" + x)
                        filesToScan = JSONData[0]
                        assistantData.dictionary["cleanData"]["possibleSubdirectories"] = list(set(assistantData.dictionary["cleanData"]["possibleSubdirectories"]).union(set(JSONData[1])))
                        filesToScan.sort() #Makes it easier as a user to pick the jsons when all the alternate versions are next to each other
                        expectedNewJSONs = len(filesToScan) #We do this again here just in case the core is being newly added to the assistant_data.json
                        if preserveData: #So we're updating a core we already have data on
                            #Remove all common values in filesToScan and list(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys()) from filesToScan
                            filesToScan = list(set(filesToScan)-set(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys()))
                            filesToScan.sort()
                            newJsonList = assistantData.dictionary["cleanData"]["cores"][x]["jsonList"]
                        if filesToScan != []:
                            print("Here's a list of all the JSON files you can pick from:")
                            for a in filesToScan:
                                print("\t" + a)
                            print("\nI will now ask you what you want these to be renamed to. If you want to hide the JSON files I mention, just press enter without inputting any text.")
                        #Scan through that folder, getting new names
                        for a in filesToScan:
                            potentialNewName = input("\t" + a + "\t")
                            if potentialNewName != "":
                                newJsonList[a] = potentialNewName #and now add it to the dictionary if the user hasn't just skipped it :)
                    
                    #Now we put our new JSON list into the assistant_data.json!
                    if newJsonList != {}:
                        assistantData.dictionary["cleanData"]["cores"][x] = {"rootfolder": currentPlatform, "jsonList": newJsonList, "expectedNewJSONs": expectedNewJSONs}
                    print("\n")
                
                #Finally, we do the actual cleaning
                if cleanCore and x in assistantData.dictionary["cleanData"]["cores"].keys():
                    
                    #By this point, whether the core is new or being updated, all that will be in the Assets/platform/core folder will be the new json files.
                    #Now, copy everything from that folder into the directory for unused json files.
                    rootFolderName = assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"]
                    mergetree("../Assets/" + rootFolderName + "/" + x, "../Assets/" + rootFolderName + "/unused_" + x)
                    if exists("../Assets/" + rootFolderName + "/" + x):
                        rmtree("../Assets/" + rootFolderName + "/" + x)
                    mkdir("../Assets/" + rootFolderName + "/" + x)
                    
                    #We also repeat the same thing for presets
                    if exists("../Presets/" + x + "/Input/"):
                        mergetree("../Presets/" + x + "/Input/" + rootFolderName + "/" + x, "../Presets/" + x + "/Input/" + rootFolderName + "/unused_" + x)
                        rmtree("../Presets/" + x + "/Input/" + rootFolderName + "/" + x)
                        mkdir("../Presets/" + x + "/Input/" + rootFolderName + "/" + x)
                    if exists("../Presets/" + x + "/Interact/"):
                        mergetree("../Presets/" + x + "/Interact/" + rootFolderName + "/" + x, "../Presets/" + x + "/Interact/" + rootFolderName + "/unused_" + x)
                        rmtree("../Presets/" + x + "/Interact/" + rootFolderName + "/" + x)
                        mkdir("../Presets/" + x + "/Interact/" + rootFolderName + "/" + x)
                    
                    #Next, anything that isn't a json or a subdirectory (e.g. license data for jotego) should get copied back to the Assets/platform/core folder.
                    for y in listdir("../Assets/" + rootFolderName + "/unused_" + x):
                        if y[y.rfind("."):] != ".json" and not isdir("../Assets/" + rootFolderName + "/unused_" + x + "/" + y):
                            move("../Assets/" + rootFolderName + "/unused_" + x + "/" + y, "../Assets/" + rootFolderName + "/" + x + "/" + y)
                    
                    #For each json file for this core that is to be renamed...
                    for y in assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys():
                    
                        #Try and find the json file in some possible subdirectory (which we collected data on earlier)
                        moveFrom = ""
                        for z in assistantData.dictionary["cleanData"]["possibleSubdirectories"]:
                            if exists("../Assets/" + rootFolderName + "/unused_" + x + "/" + z + y + ".json"):
                                moveFrom = rootFolderName + "/unused_" + x + "/" + z + y + ".json"
                                break
                        
                        #If we found the file, then rename and move it.
                        if moveFrom != "":
                            move("../Assets/" + moveFrom, "../Assets/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json")
                            
                            #Plus do the same for Presets!
                            if exists("../Presets/" + x + "/Input/"):
                                moveFrom = ""
                                for z in assistantData.dictionary["cleanData"]["possibleSubdirectories"]:
                                    if exists("../Presets/" + x + "/Input/" + rootFolderName + "/unused_" + x + "/" + z + y + ".json"):
                                        moveFrom = "../Presets/" + x + "/Input/" + rootFolderName + "/unused_" + x + "/" + z + y + ".json"
                                        break
                                if moveFrom != "":
                                    move(moveFrom, "../Presets/" + x + "/Input/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json")
                            if exists("../Presets/" + x + "/Interact/"):
                                moveFrom = ""
                                for z in assistantData.dictionary["cleanData"]["possibleSubdirectories"]:
                                    if exists("../Presets/" + x + "/Interact/" + rootFolderName + "/unused_" + x + "/" + z + y + ".json"):
                                        moveFrom = "../Presets/" + x + "/Interact/" + rootFolderName + "/unused_" + x + "/" + z + y + ".json"
                                        break
                                if moveFrom != "":
                                    move(moveFrom, "../Presets/" + x + "/Interact/" + rootFolderName + "/" + x + "/" + assistantData.dictionary["cleanData"]["cores"][x]["jsonList"][y] + ".json")
                        
                        else:
                            print("We can't find " + y + ".json in any possible subdirectory! So we haven't copied that after all.")
                            system("pause") #so they can read that
                            
            assistantData.save()

#FIX PLATFORM DATA
def fix_platform():
    for x in listdir("../Platforms"):
        if x[x.rfind(".")+1:] == "json": #Check all platform jsons
            system("cls")
            print("Fixing platform data...\n\t" + x[0:x.rfind(".")])
        
            platformData = OpenJSON("../Platforms/" + x, encodeAsUTF8 = True)
            if not platformData.dictionary["platform"]["category"] in assistantData.dictionary["platformFixData"]["acceptedCategories"] and not platformData.dictionary["platform"]["category"] in assistantData.dictionary["platformFixData"]["unacceptedCategories"] and not platformData.dictionary["platform"]["category"] == assistantData.dictionary["favouriteData"]["categoryName"]:
                # We check if the platform category is completely new to us - neither an accepted nor unaccepted category, and also not the user-picked "favCategoryName" for favourite cores
                print("It looks like the " + x[0:x.rfind(".")] + " core has a category this program hasn't seen before in its platform data! That category is " + platformData.dictionary["platform"]["category"] + ".")
                while True:
                    # Sort it into either accepted or unaccepted categories
                    userInput = input("Should we...\n\t1. Allow cores with that platform data?\n\t2. Always prompt you to edit platform data when we see that category?\n\t(1/2) ")
                    if userInput == "1":
                        assistantData.dictionary["platformFixData"]["acceptedCategories"].append(platformData.dictionary["platform"]["category"])
                        break
                    elif userInput == "2":
                        assistantData.dictionary["platformFixData"]["unacceptedCategories"].append(platformData.dictionary["platform"]["category"])
                        break
                    else:
                        print("Invalid input.")
                        
            # If it's unaccepted at this stage (whether because we just rejected it or not) then prompt the user to replace it with make_platform_data
            if platformData.dictionary["platform"]["category"] in assistantData.dictionary["platformFixData"]["unacceptedCategories"]:
                platformData.dictionary["platform"] = make_platform_data(x[0:x.rfind(".")])
                platformData.save()

#CLONE CORES
def clone_cores():
    for x in listdir("../Cores"):
        if isdir("../Cores/" + x) and x in assistantData.dictionary["cleanData"]["cores"].keys():
        
            #If there's more than 1 game attached to this core (after cleaning), and the first clone core doesn't yet exist...
            if len(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].keys()) > 1 and not exists("../Cores/clones." + x[x.find(".")+1:] + "1"):
                system("cls")
                print("Cloning cores...\n\t" + x)
                #That last if has to be on a separate line, or else you get a keyerror when it's not in assistantData.dictionary["cleanData"]["cores"]
                
                #Now - find out which of the games the core is actually named after using the Platforms data
                platformData = OpenJSON("../Platforms/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + ".json", encodeAsUTF8 = True)
                realGame = platformData.dictionary["platform"]["name"]
                
                if not x in assistantData.dictionary["cloneData"]["skip"]:
                    # Check if we're skipping this core
                    directory = listdir("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x)
                    
                    if not (realGame + ".json") in directory:
                        # We check if the name of the platform is also the name of a game. If not, we prompt for the platform to be renamed until it is the name of a game.
                        print("\nWe've noticed that the " + x + " core has the platform name " + realGame + ", but for this program we want it to be one of the game JSONs attached to the core. So it can be any of the following:")
                        directoryJSONs = scan_for_JSONs("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x)[0]
                        for y in directoryJSONs:
                            print("\t" + y)
                        while True:
                            realGame = input("\nWhich do you want it to be? (It's best to choose whichever one is linked to the core's platform image!)")
                            if (realGame+".json") in directory:
                                platformData.dictionary["platform"]["name"] = realGame
                                break
                            else:
                                print("Invalid input.")
                    platformData.save()
                    
                    # We don't need to worry about the game with the same name as the core platform now - because after moving all the others out, that one will be the only game left
                    # Also don't bother with things that aren't JSON files of course.
                    directory.remove(realGame + ".json")
                    for y in directory:
                        if y[y.rfind("."):] != ".json":
                            directory.remove(y)
                            
                    for y in range(len(directory)): # Now - for all the other games...
                        #Make a platform image! (We do this first because if there's an error here, restarting the program will still work fine)
                        make_image(directory[y][0:directory[y].rfind(".")])
                        #Then put that image in the right place
                        copy("../Updater/_assistantimages/" + directory[y][0:directory[y].rfind(".")] + ".bin", "../Platforms/_images/" + x[x.find(".")+1:] + str(y+1) + ".bin")
                        
                        #Actually make a copy of the core called "clones.[corename][number]"
                        copytree("../Cores/" + x, "../Cores/clones" + x[x.find("."):] + str(y+1))
                        
                        #Change the core data to have the authorname clones, and the platform id [corename][number]
                        coreJSON = OpenJSON("../Cores/clones" + x[x.find("."):] + str(y+1) + "/core.json")
                        coreJSON.dictionary["core"]["metadata"]["author"] = "clones"
                        coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] = coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + str(y+1)
                        coreJSON.dictionary["core"]["metadata"]["shortname"] = coreJSON.dictionary["core"]["metadata"]["shortname"] + str(y+1)
                        coreJSON.save()
                        
                        #Make a new Assets folder called [corename][number], and copy the json file to the subfolder "clones.[corename][number]"
                        #So the json file is now in e.g. Assets/jtaliens1/clones.jtaliens1
                        mkdir("../Assets/" + x[x.find(".")+1:] + str(y+1))
                        mkdir("../Assets/" + x[x.find(".")+1:] + str(y+1) + "/clones." + x[x.find(".")+1:] + str(y+1))
                        mkdir("../Assets/" + x[x.find(".")+1:] + str(y+1) + "/common")
                        move("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x + "/" + directory[y], "../Assets/" + x[x.find(".")+1:] + str(y+1) + "/clones." + x[x.find(".")+1:] + str(y+1) + "/" + directory[y])
                        
                        #Open the json file itself and check which rom it uses, then copy that if present to "common"
                        #I used to move the roms, but that caused issues with the beta.bin file for jotego beta cores, which really needs to be in every clone core common folder.
                        gameJSON = OpenJSON("../Assets/" + x[x.find(".")+1:] + str(y+1) + "/clones." + x[x.find(".")+1:] + str(y+1) + "/" + directory[y])
                        for z in gameJSON.dictionary["instance"]["data_slots"]:
                            if exists("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/common/" + z["filename"]):
                                copy("../Assets/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/common/" + z["filename"], "../Assets/" + x[x.find(".")+1:] + str(y+1) + "/common/" + z["filename"])
                        
                        #Check if it needs presets and do the same for them if so
                        if exists("../Presets/" + x + "/Input/") or exists("../Presets/" + x + "/Interact/"):
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1))
                        if exists("../Presets/" + x + "/Input/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x + "/" + directory[y]):
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1) + "/Input/")
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1) + "/Input/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1))
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1) + "/Input/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1) + "/clones" + x[x.find("."):] + str(y+1))
                            move("../Presets/" + x + "/Input/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x + "/" + directory[y], "../Presets/clones" + x[x.find("."):] + str(y+1) + "/Input/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1) + "/clones" + x[x.find("."):] + str(y+1) + "/" + directory[y])
                        if exists("../Presets/" + x + "/Interact/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x + "/" + directory[y]):
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1) + "/Interact/")
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1) + "/Interact/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1))
                            mkdir("../Presets/clones" + x[x.find("."):] + str(y+1) + "/Interact/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1) + "/clones" + x[x.find("."):] + str(y+1))
                            move("../Presets/" + x + "/Interact/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + "/" + x + "/" + directory[y], "../Presets/clones" + x[x.find("."):] + str(y+1) + "/Interact/" + assistantData.dictionary["cleanData"]["cores"][x]["rootfolder"] + str(y+1) + "/clones" + x[x.find("."):] + str(y+1) + "/" + directory[y])
                        
                        #Then create platform data - reuse the name of the json for the name of the core, and the category, publisher and year of release from the original
                        newPlatformData = OpenJSON("../Platforms/" + x[x.find(".")+1:] + str(y+1) + ".json", encodeAsUTF8 = True, dictionary = {"platform": {"category":platformData.dictionary["platform"]["category"],"name":directory[y][0:directory[y].rfind(".")],"year":platformData.dictionary["platform"]["year"],"manufacturer":platformData.dictionary["platform"]["manufacturer"]}})
                        newPlatformData.save()

#INTEGER SCALE CORES
def integer_scale():
    for x in listdir("../Cores"):
        system("cls")
        print("Scaling cores...\n\t" + x)
    
        # If we're looking at a favourite core, just copy the settings from the original core
        # We don't do this for clone cores or alternate cores, because in some cases we'll actually want different options for them (especially with regards to screen rotation)
        coreName = x
        if x[0:6] == "faves.":
            coreName = assistantData.dictionary["favouriteData"]["cores"][x[6:]][0]
        
        # Now, if the core we're checking isn't singled out in useOriginalRatio...
        if isdir("../Cores/" + x) and not coreName in assistantData.dictionary["aspectData"]["useOriginalRatio"]:
            
            #Open bits and bobs
            videoJSON = OpenJSON("../Cores/" + x + "/video.json")
            coreJSON = OpenJSON("../Cores/" + x + "/core.json")
            platformJSON = OpenJSON("../Platforms/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + ".json", encodeAsUTF8 = True)

            for y in range(len(videoJSON.dictionary["video"]["scaler_modes"])):
                # Integer scale everything
                videoJSON.dictionary["video"]["scaler_modes"][y]["aspect_w"] = videoJSON.dictionary["video"]["scaler_modes"][y]["width"]
                videoJSON.dictionary["video"]["scaler_modes"][y]["aspect_h"] = videoJSON.dictionary["video"]["scaler_modes"][y]["height"]
                # If we've got a custom ratio, then write that in the right place in the videoJSON (by confirming the height and width values match)
                if coreName in assistantData.dictionary["aspectData"]["useCustomRatio"].keys():
                    for z in assistantData.dictionary["aspectData"]["useCustomRatio"][coreName]:
                        if z["height"] == videoJSON.dictionary["video"]["scaler_modes"][y]["height"] and z["width"] == videoJSON.dictionary["video"]["scaler_modes"][y]["width"]:
                            videoJSON.dictionary["video"]["scaler_modes"][y]["aspect_h"] = z["aspect_h"]
                            videoJSON.dictionary["video"]["scaler_modes"][y]["aspect_w"] = z["aspect_w"]
                            
            # Also, check the platform name against the lists to rotate by different amounts, and rotate as necessary
            if platformJSON.dictionary["platform"]["name"] in assistantData.dictionary["aspectData"]["rotateBy90"]:
                videoJSON.dictionary["video"]["scaler_modes"][0]["rotation"] = 90
            if platformJSON.dictionary["platform"]["name"] in assistantData.dictionary["aspectData"]["rotateBy180"]:
                videoJSON.dictionary["video"]["scaler_modes"][0]["rotation"] = 180
            elif platformJSON.dictionary["platform"]["name"] in assistantData.dictionary["aspectData"]["rotateBy270"]:
                videoJSON.dictionary["video"]["scaler_modes"][0]["rotation"] = 270
                
            videoJSON.save()

#AUTOSTART CORES
def autostart_cores():
    for x in listdir("../Cores"):
        if isdir("../Cores/" + x): #check core exists
            system("cls")
            print("Autostarting cores...\n\t" + x)

            # We're going to try and look for the jsonFile in a few places. If we're unsuccessful, it will stay a blank string, and so we know there is no jsonFile to autostart.
            jsonFile = ""
            
            # Open the relevant core and platform jsons
            coreJSON = OpenJSON("../Cores/" + x + "/core.json")
            platformJSON = OpenJSON("../Platforms/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + ".json", encodeAsUTF8 = True)
            
            if x in assistantData.dictionary["cleanData"]["cores"].keys() and len(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"]) == 1:
                #take from clean_assets data, if there's only one json file listed there
                jsonFile = list(assistantData.dictionary["cleanData"]["cores"][x]["jsonList"].values())[0] + ".json"
            elif x[0:x.find(".")] == "clones":
                #Or, if it's a clone core we know already that that can only have one json file attached to it, so we just grab that
                jsonFile = listdir("../Assets/" + coreJSON.dictionary["core"]["metadata"]["shortname"] + "/" + x)[0]
            elif exists("../Assets/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + x + "/" + platformJSON.dictionary["platform"]["name"] + ".json"):
                #otherwise, we can do our best and just autostart the game that has the same title as the core does (read from the platform data) - provided that json file exists
                jsonFile = platformJSON.dictionary["platform"]["name"] + ".json"
            
            #If we've now got a json file, and we haven't singled out this core on the noAutoStartList...
            if jsonFile != "" and not platformJSON.dictionary["platform"]["name"] in assistantData.dictionary["autostartData"]["skip"]:
                
                # We want to fuse aspects of the game's json file and the core's data.json.
                dataJSON = OpenJSON("../Cores/" + x + "/data.json")
                gameJSON = OpenJSON("../Assets/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + x + "/" + jsonFile)
                
                newDataSlots = []
                for y in gameJSON.dictionary["instance"]["data_slots"]:
                    # Go through each data slot, check if the game JSON has information to fill that slot with, and if so include that data slot
                    # This will mean we don't include the data slot for the JSON itself - which is good
                    activeDataSlot = [a for a in dataJSON.dictionary["data"]["data_slots"] if a["id"] == y["id"]]
                    if activeDataSlot != []:
                        activeDataSlot = activeDataSlot[0]
                        if exists("../Assets/" + coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/common/" + y["filename"]):
                            newDataSlots.append({"id": activeDataSlot["id"], "name": activeDataSlot["name"], "required": True, "parameters": activeDataSlot["parameters"], "filename": y["filename"], "address": activeDataSlot["address"]})
                        else:
                            newDataSlots.append({"id": activeDataSlot["id"], "name": activeDataSlot["name"], "required": False, "parameters": activeDataSlot["parameters"], "filename": y["filename"], "address": activeDataSlot["address"]})
                
                # Now write the new data slots into the data JSON
                dataJSON.dictionary["data"]["data_slots"] = newDataSlots
                dataJSON.save()
                # And deal with presets (usually linked to the JSON file) by copying them in as input.json or interact.json
                if exists("../Presets/" + x + "/Input/" + coreJSON.dictionary["core"]["metadata"]["shortname"] + "/" + x + "/" + jsonFile):
                    copy("../Presets/" + x + "/Input/" + coreJSON.dictionary["core"]["metadata"]["shortname"] + "/" + x + "/" + jsonFile, "../Cores/" + x + "/input.json")
                if exists("../Presets/" + x + "/Interact/" + coreJSON.dictionary["core"]["metadata"]["shortname"] + "/" + x + "/" + jsonFile):
                    copy("../Presets/" + x + "/Interact/" + coreJSON.dictionary["core"]["metadata"]["shortname"] + "/" + x + "/" + jsonFile, "../Cores/" + x + "/interact.json")

#RENAME CORE PLATFORMS
def rename_core_platforms():
    for x in assistantData.dictionary["platformRenameData"].keys(): #For each core in renamePlatformDict...
        system("cls")
        print("Renaming core platforms...\n\t" + x)
        
        if isdir("../Cores/" + x): #check the core exists
            coreJSON = OpenJSON("../Cores/" + x + "/core.json")
            
            #If it's not already been renamed, then...
            if not coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] == assistantData.dictionary["platformRenameData"][x]:
                
                #This is the old platform name
                oldPlatform = coreJSON.dictionary["core"]["metadata"]["platform_ids"][0]
                
                #Rename the platform ID in the core data
                coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] = assistantData.dictionary["platformRenameData"][x]
                coreJSON.save()
                            
                for y in listdir("../Cores/"):
                    if isdir("../Cores/" + y):
                        coreJSON = OpenJSON("../Cores/" + y + "/core.json")
                        #If another core has the same platform as what this core used to have...
                        if coreJSON.dictionary["core"]["metadata"]["platform_ids"][0] == oldPlatform:
                            #Then we take care to only move this core's data over to the new platform.
                            if exists("../Assets/" + oldPlatform + "/" + x):
                                mergetree("../Assets/" + oldPlatform + "/" + x, "../Assets/" + assistantData.dictionary["platformRenameData"][x] + "/" + x)
                                rmtree("../Assets/" + oldPlatform + "/" + x)
                                break
                                
                # If there's still a directory for this core in the old platform's asset folder at this stage, that means this is the only core with this platform.
                if isdir("../Assets/" + oldPlatform + "/" + x):
                    # So we destroy all trace of the old platform!!!
                    
                    # Move the assets folder over to the new platform
                    mergetree("../Assets/" + oldPlatform, "../Assets/" + assistantData.dictionary["platformRenameData"][x])
                    rmtree("../Assets/" + oldPlatform)
                    
                    # Rename the old platform data to the new platform, or delete it if we've already got stuff for the new platform
                    if exists("../Platforms/" + oldPlatform + ".json") and not exists("../Platforms/" + assistantData.dictionary["platformRenameData"][x] + ".json"):
                        rename("../Platforms/" + oldPlatform + ".json", "../Platforms/" + assistantData.dictionary["platformRenameData"][x] + ".json")
                    elif exists("../Platforms/" + assistantData.dictionary["platformRenameData"][x] + ".json"):
                        remove("../Platforms/" + oldPlatform + ".json")
                    
                    # Same with the platform image
                    if exists("../Platforms/_images/" + oldPlatform + ".bin") and not exists("../Platforms/_images/" + assistantData.dictionary["platformRenameData"][x] + ".bin"):
                        rename("../Platforms/_images/" + oldPlatform + ".bin", "../Platforms/_images/" + assistantData.dictionary["platformRenameData"][x] + ".bin")
                    
                    # Deal with Presets folder
                    if exists("../Presets/" + x + "/Input/" + oldPlatform):
                        mergetree("../Presets/" + x + "/Input/" + oldPlatform, "../Presets/" + x + "/Input/" + assistantData.dictionary["platformRenameData"][x])
                    if exists("../Presets/" + x + "/Interact/" + oldPlatform):
                        mergetree("../Presets/" + x + "/Interact/" + oldPlatform, "../Presets/" + x + "/Interact/" + assistantData.dictionary["platformRenameData"][x])
                    
                    # Finally, if we have asset cleaning turned on, then also replace all instances of the old platform with the new one!
                    for y in assistantData.dictionary["cleanData"]["cores"].keys():
                        if assistantData.dictionary["cleanData"]["cores"][y]["rootfolder"] == oldPlatform:
                            assistantData.dictionary["cleanData"]["cores"][y]["rootfolder"] = assistantData.dictionary["platformRenameData"][x]

#CREATE FAVOURITE CORES
def create_favourite_cores():
    #Prompt for a name for the category, if it doesn't already exist
    if assistantData.dictionary["favouriteData"]["categoryName"] == "":
        assistantData.dictionary["favouriteData"]["categoryName"] = input("What category name do you want your favourite cores to be bundled under? Examples include \"Favourites\", \"Favorites\" (if you're a darned American!!!), or \"Faves\" (if you're in a rush, or want to please everyone).\n")
    
    #For each entry in the list of favourite games...
    for x in assistantData.dictionary["favouriteData"]["cores"].keys():
        if isdir("../Cores/" + assistantData.dictionary["favouriteData"]["cores"][x]): #check the core actually exists
            system("cls")
            print("Creating favourite cores...\n\tfaves." + x)
            
            #Check for the scenario where the favourite core exists already, AND is based on a core that has since been updated, and then remove the core so it can be remade
            if isdir("../Cores/faves." + x):
                if compare_core_release(assistantData.dictionary["favouriteData"]["cores"][x][0], "faves." + x):
                    rmtree("../Cores/faves." + x)
            
            #We now open the base core JSON, to get information on where the asset would be
            originalCoreJSON = OpenJSON("../Cores/" + assistantData.dictionary["favouriteData"]["cores"][x][0] + "/core.json")
            if len(assistantData.dictionary["favouriteData"]["cores"][x][1]) > 31: #Filenames for the AP must be less than 32 characters long - so we don't try and make the core if it's longer than that
                print("You've listed " + assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")] + " as a favourite game! Unfortunately, its filename is too long to be autostarted by the Pocket. Please rename it so the full filename, including extension, is 31 characters or less! And don't forget to do the same to any save data and the assistant_data.json :)")
            elif not isdir("../Cores/faves." + x) and isfile("../Assets/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/common/" + assistantData.dictionary["favouriteData"]["cores"][x][1]):
                
                #We're now making the favourite core from scratch - so make the image, download any assets with pocket_updater.exe, and copy the core's directory itself over
                make_image(assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")])
                copy("../Updater/_assistantimages/" + assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")] + ".bin", "../Platforms/_images/" + x + ".bin")
                system("pocket_updater.exe assets -p ../ -c " + assistantData.dictionary["favouriteData"]["cores"][x][0])
                copytree("../Cores/" + assistantData.dictionary["favouriteData"]["cores"][x][0], "../Cores/faves." + x)
                
                #Now we set up the core JSON file
                coreJSON = OpenJSON("../Cores/faves." + x + "/core.json")
                coreJSON.dictionary["core"]["metadata"]["platform_ids"].append(x) #This means the fave-core will have its original platform ID first, which means when we autostart it from its individual platform ID, it loads the assets from the original folder - basically meaning the save data is preserved
                coreJSON.dictionary["core"]["metadata"]["author"] = "faves"
                coreJSON.dictionary["core"]["metadata"]["shortname"] = x
                coreJSON.save()

                #Next, the data JSON file.
                dataJSON = OpenJSON("../Cores/faves." + x + "/data.json")
                for y in range(len(dataJSON.dictionary["data"]["data_slots"])):
                    #Check through the data slots of the original core to see if there were any required files then (e.g. bios). If so, make a folder for the fave-core if necessary and copy over the old files.
                    if "filename" in dataJSON.dictionary["data"]["data_slots"][y].keys():
                        if isdir("../Assets/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + assistantData.dictionary["favouriteData"]["cores"][x][0]) and not isdir("../Assets/" + originalCoreJSON["core"]["metadata"]["platform_ids"][0] + "/faves." + x):
                            mkdir("../Assets/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/faves." + x)
                        if isdir("../Assets/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + assistantData.dictionary["favouriteData"]["cores"][x][0]):
                            copy("../Assets/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/" + assistantData.dictionary["favouriteData"]["cores"][x][0] + "/" + dataJSON.dictionary["data"]["data_slots"][y]["filename"],"../Assets/" + originalCoreJSON["core"]["metadata"]["platform_ids"][0] + "/faves." + x + "/" + dataJSON.dictionary["data"]["data_slots"][y]["filename"])
                for y in range(len(dataJSON.dictionary["data"]["data_slots"])):
                    #If there was previously a JSON file to load (for e.g. arcade games), we remove it from the data slot list (because we're now loading the rom directly anyway)
                    if "json" in dataJSON.dictionary["data"]["data_slots"][y]["extensions"]:
                        dataJSON.dictionary["data"]["data_slots"] = dataJSON.dictionary["data"]["data_slots"][0:y] + dataJSON.dictionary["data"]["data_slots"][y+1:]
                        break
                for y in range(len(dataJSON.dictionary["data"]["data_slots"])):
                    #Next, check for the data slot that accepts the file extension of the provided rom for this favourite core, and set the filename to that provided rom
                    if assistantData.dictionary["favouriteData"]["cores"][x][1][assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")+1:] in dataJSON.dictionary["data"]["data_slots"][y]["extensions"]:
                        dataJSON.dictionary["data"]["data_slots"][y]["filename"] = assistantData.dictionary["favouriteData"]["cores"][x][1]
                if isdir("../Saves/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0]):
                    #If there's save data for the favourited game, then we also provide the save data slot with the corresponding save filename
                    for y in range(len(dataJSON.dictionary["data"]["data_slots"])):
                        if "sav" in dataJSON.dictionary["data"]["data_slots"][y]["extensions"]:
                            dataJSON.dictionary["data"]["data_slots"][y]["filename"] = assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")] + ".sav"
                #Finally, if there is a Presets folder attached to the original game and core, then copy that to this core too
                if exists("../Presets/" + assistantData.dictionary["favouriteData"]["cores"][x][0] + "/Input/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/common/" + assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")] + ".json"):
                    copy("../Presets/" + assistantData.dictionary["favouriteData"]["cores"][x][0] + "/Input/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/common/" + assistantData.dictionary["favouriteData"]["cores"][x][1],"../Cores/faves." + x + "/input.json")
                if exists("../Presets/" + assistantData.dictionary["favouriteData"]["cores"][x][0] + "/Interact/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/common/" + assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")] + ".json"):
                    copy("../Presets/" + assistantData.dictionary["favouriteData"]["cores"][x][0] + "/Interact/" + originalCoreJSON.dictionary["core"]["metadata"]["platform_ids"][0] + "/common/" + assistantData.dictionary["favouriteData"]["cores"][x][1],"../Cores/faves." + x + "/interact.json")
                dataJSON.save()
                
                #And also make platform data if there's not data there already!
                if not exists("../Platforms/" + x + ".json"):
                    platformJSON = {"platform": make_platform_data(assistantData.dictionary["favouriteData"]["cores"][x][1][0:assistantData.dictionary["favouriteData"]["cores"][x][1].rfind(".")],assistantData.dictionary["favouriteData"]["categoryName"])}
                    a = open("../Platforms/" + x + ".json","w")
                    json.dump(platformJSON, a, indent = 4)
                    a.close()
                
                #Since we've already downloaded the assets, we don't need to do it every time we run pocket_updater
                dont_download_assets("faves." + x)

#CREATE ALT CORES
def create_alt_cores():
    for x in assistantData.dictionary["altCoreData"].keys(): #For all the cores in the altCoreList...
        system("cls")
        print("Creating alternate core versions...\n\t" + x)
        
        #Remove the altversion if the core it's based on has been updated
        if isdir("../Cores/" + x):
            if compare_core_release(assistantData.dictionary["altCoreData"][x],x):
                rmtree("../Cores/" + x)
        if not isdir("../Cores/" + x) and isdir("../Cores/" + assistantData.dictionary["altCoreData"][x]):
            #Copy the core over
            copytree("../Cores/" + assistantData.dictionary["altCoreData"][x], "../Cores/" + x)
            coreJSON = OpenJSON("../Cores/" + x + "/core.json")
            #Then copy any assets (e.g. bios) from the original core's assets/platform/core folder into a new one for this core
            for y in coreJSON.dictionary["core"]["metadata"]["platform_ids"]:
                if isdir("../Assets/" + y + "/" + assistantData.dictionary["altCoreData"][x]) and not isdir("../Assets/" + y + "/" + x):
                    mkdir("../Assets/" + y + "/" + x)
            #Also change the shortname to whatever the user's set it to
            coreJSON.dictionary["core"]["metadata"]["shortname"] = x[x.rfind(".")+1:]
            coreJSON.save()
            #And download stuff once, then blacklist it from the updater (because you may want to create altversions for different bioses, e.g. super game boy 2 or vw)
            system("pocket_updater.exe assets -p ../ -c " + x)
            dont_download_assets(x)

def assist():
    #Check if the user wants to do each possible job, then do them if so!
    if assistantData.dictionary["programSettings"]["rename"]:
        rename_core_platforms()
    if assistantData.dictionary["programSettings"]["clean"]:
        clean_assets()
    if assistantData.dictionary["programSettings"]["platforms"]:
        fix_platform()
    if assistantData.dictionary["programSettings"]["clone"]:
        clone_cores()
    if assistantData.dictionary["programSettings"]["altcores"]:
        create_alt_cores()
    if assistantData.dictionary["programSettings"]["favourites"]:
        create_favourite_cores()
    if assistantData.dictionary["programSettings"]["aspect"]:
        integer_scale()
    if assistantData.dictionary["programSettings"]["autostart"]:
        autostart_cores()

def main():
    system("title Pocket Assistant! :)")
    #First check for some required bits and bobs
    if isfile("../Updater/_assistantimages/Analogue-Pocket-Image-Process-master/package.json") and isfile("pocket_updater.exe"):
        #If necessary, create assistant_data.json
        baseAssistantData = {"platformFixData": {"acceptedCategories": [],"unacceptedCategories": []},"altCoreData": {},"aspectData": {"rotateBy180": [],"rotateBy270": [],"rotateBy90": [],"useCustomRatio": {"agg23.PC Engine": [{"aspect_h": 240,"aspect_w": 256,"height": 240,"width": 512},{"aspect_h": 224,"aspect_w": 256,"height": 224,"width": 512}]},"useOriginalRatio": ["Spiritualized.VideoBrain","agg23.SNES","boogermann.supervision","Spiritualized.Adventurevision","Mazamars312.Amiga","ericlewis.SuperBreakout","jotego.jtcps1","jotego.jtcps15"]},"favouriteData": {"cores": {},"categoryName": ""},"cleanData": {"skip": ["Mazamars312.PC Engine CD"],"cores": {},"possibleSubdirectories": [""],"versionList": {}},"autostartData": {"skip": []},"programSettings": {},"platformRenameData": {},"cloneData": {"skip": ["jotego.jtcps2","jotego.jtcps15","jotego.jtcps1","Mazamars312.NeoGeo","Mazamars312.NeoGeo_Overdrive"]}}
        global assistantData
        setup_data(baseAssistantData)
        
        #Now open assistant_data.json!
        assistantData = OpenJSON("assistant_data.json")
        
        #If we're running it in express mode, then just assist()
        if len(sys.argv) > 1:
            if sys.argv[1] == "express":
                assist()
        else:
            #Otherwise show a cute little menu!
            displayDictionary = {True: "on", False: "off"}
            while True:
                system("cls")
                print("Hello! I am your Pocket Assistant. Beep boop. What do you want me to do?\n\n\t1. Assist!\n\t2. Edit data on what I should do\n\t3. Remake certain platform images\n\t4. Clear part or all of the program's data to rerun setup\n\t5. Exit")
                action = input()
                if action == "1": #Assist!
                    system("cls")
                    assist()
                    break
                elif action == "2": #Edit saved assistant data and settings
                    while True:
                        system("cls")
                        print("Which settings would you like to change?\n\n\t1. Which jobs I do in an \"assist\"\n\t2. Which games you want listed as \"favourites\"\n\t3. Which cores you want alternate versions generated for\n\t4. Which games you DON'T want autostarted\n\t5. Which cores you DON'T want cleaned\n\t6. Which cores you DON'T want cloned for each JSON file\n\t7. Which platforms you want renamed\n\t8. Aspect ratio data\n\nOr just press Enter to go back!")
                        action = input()
                        if action == "1": # which jobs in an assist
                            while True:
                                system("cls")
                                print("Here are the things I can do:\n")
                                print("\t1. Asset cleaning (when you download or update a core that comes with JSON files, this will hide the JSONs you don't want automatically).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["clean"]] + "\n")
                                print("\t2. Core cloning (when you have a core with multiple JSON files, this will make copies of the core so each JSON has its own core - this requires asset cleaning).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["clone"]]+ "\n")
                                print("\t3. Autostart (for all supported cores - which is most of them - if you only have one JSON file in the directory, this will make the core automatically load it - this requires asset cleaning).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["autostart"]]+ "\n")
                                print("\t4. Platform cleaning (when you download a core with an unusual category, this will prompt you for help putting it in the right place).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["platforms"]]+ "\n")
                                print("\t5. Aspect ratio correction (this will integer scale all cores, except for any you tell us not to).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["aspect"]]+ "\n")
                                print("\t6. Rename core platforms (this will change the associated platform for any core you ask us to).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["rename"]]+ "\n")
                                print("\t7. Generate favourite cores (this will create copies of cores that automatically start any specific game you want).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["favourites"]]+ "\n")
                                print("\t8. Generate alt cores (this will create alternate versions of cores, for when you want to switch between e.g. different BIOS files or video modes on device).\n\tCurrently turned " + displayDictionary[assistantData.dictionary["programSettings"]["altcores"]]+ "\n")
                                print("\t... Or press Enter to save and return to the last menu!")
                                action = input()
                                if action == "1" and assistantData.dictionary["programSettings"]["clean"]:
                                    assistantData.dictionary["programSettings"]["clean"] = False
                                    assistantData.dictionary["programSettings"]["autostart"] = False
                                    assistantData.dictionary["programSettings"]["clone"] = False #several change here because they're dependent on asset cleaning being turned on
                                elif action == "1":
                                    assistantData.dictionary["programSettings"]["clean"] = True
                                if action == "4":
                                    assistantData.dictionary["programSettings"]["platforms"] = not assistantData.dictionary["programSettings"]["platforms"]
                                if action == "2" and assistantData.dictionary["programSettings"]["clean"]:
                                    assistantData.dictionary["programSettings"]["clone"] = not assistantData.dictionary["programSettings"]["clone"]
                                if action == "5":
                                    assistantData.dictionary["programSettings"]["aspect"] = not assistantData.dictionary["programSettings"]["aspect"]
                                if action == "6":
                                    assistantData.dictionary["programSettings"]["rename"] = not assistantData.dictionary["programSettings"]["rename"]
                                if action == "3" and assistantData.dictionary["programSettings"]["clean"]:
                                    assistantData.dictionary["programSettings"]["autostart"] = not assistantData.dictionary["programSettings"]["autostart"]
                                if action == "7":
                                    assistantData.dictionary["programSettings"]["favourites"] = not assistantData.dictionary["programSettings"]["favourites"]
                                if action == "8":
                                    assistantData.dictionary["programSettings"]["altcores"] = not assistantData.dictionary["programSettings"]["altcores"]
                                if action == "":
                                    assistantData.save()
                                    break
                        elif action == "2": #list of favourites
                            while True:
                                system("cls")
                                print("Here is the current list of favourite cores:")
                                for x in assistantData.dictionary["favouriteData"]["cores"].keys():
                                    print("\t" + x + ", from base core " + assistantData.dictionary["favouriteData"]["cores"][x][0] + " using ROM file " + assistantData.dictionary["favouriteData"]["cores"][x][1])
                                print("\nPlease give us a shortname for a favourites core. If it's already in our database, we'll remove it. If not, we'll add it. Or, just press Enter to go back!")
                                action = input("")
                                if action == "":
                                    break
                                elif action in assistantData.dictionary["favouriteData"]["cores"].keys():
                                    assistantData.dictionary["favouriteData"]["cores"].pop(action)
                                else:
                                    coreName = input("\nWhich core should this game use? Please enter the core name as listed in the Cores/ directory, e.g. Spiritualized.SuperGB\n")
                                    romName = input("\nWhich rom should this game use? Please enter a rom from the common asset folder associated with this core, including extension, e.g. Super Mario Bros. Deluxe.gbc\nNote: The Pocket only supports filenames up to 31 characters, so beware!")
                                    if len(romName) > 31:
                                        print("Sorry! The ROM name is too long. Please rename and try again!")
                                    else:
                                        assistantData.dictionary["favouriteData"]["cores"][action] = [coreName, romName]
                        elif action == "3": #cores to generate altcores for
                            assistantData.dictionary["altCoreData"] = edit_dict(assistantData.dictionary["altCoreData"], "alternate versions of cores to generate", "Please enter the name you'd like to give the alternate version of the core, as it would be listed in the Cores/ directory, e.g. pram0d.garegga-TATE or Spiritualized.SuperGB2. If it's already in our list we'll remove it, otherwise we'll add it!", "Please enter the name of the core that this is an alternate version of, as it would be listed in the Cores/ directory, e.g. pram0d.garegga or Spiritualized.SuperGB")
                        elif action == "4": #cores to NOT autostart the only JSON file for
                            assistantData.dictionary["autostartData"]["skip"] = edit_list(assistantData.dictionary["autostartData"]["skip"], "cores that you DON'T want autostarted", "Please enter the platform name that corresponds to the core, e.g. Contra. \nNote: any core that has multiple JSON files attached to it will automatically be skipped.")
                        elif action == "5": #cores NOT to clean
                            assistantData.dictionary["cleanData"]["skip"] = edit_list(assistantData.dictionary["cleanData"]["skip"], "cores that you DON'T want cleaned", "Please enter the core name as listed in the Cores/ directory, e.g. jotego.jtaliens\nNote: cores not containing JSON files, such as console cores, will automatically not be cleaned.")
                        elif action == "6": #cores NOT to clone for each JSON file
                            assistantData.dictionary["cloneData"]["skip"] = edit_list(assistantData.dictionary["cloneData"]["skip"], "cores that you DON'T want cloned for each JSON file", "Please enter the core name as listed in the Cores/ directory, e.g. jotego.jtaliens.")
                        elif action == "7": #platforms to rename
                            assistantData.dictionary["platformRenameData"] = edit_dict(assistantData.dictionary["platformRenameData"], "platforms to rename", "Please enter the core whose platform you want to rename, as listed in the Cores/ directory, e.g. jotego.jtcps1. If it's already in our list we'll remove it, otherwise we'll add it!", "Please enter what you want to rename its platform to, e.g. \"cps1\".\nNote: this is the platform as it will be used in, for instance, the Assets folder - not the platform name, which is listed in the Analogue Pocket's own openFPGA menu.")
                        elif action == "8": #aspect ratio data
                            while True:
                                system("cls")
                                print("Here is the aspect ratio data you can edit:\n\n\t1. Games to NOT adjust the aspect ratio of at all\n\t2. Games with custom aspect ratios (ie. not integer scaled)\n\t3. Games to rotate by 90 degrees\n\t4. Games to rotate by 180 degrees\n\t5. Games to rotate by 270 degrees\n\nOr just press Enter to go back!")
                                action = input()
                                if action == "1":
                                    assistantData.dictionary["aspectData"]["useOriginalRatio"] = edit_list(assistantData.dictionary["aspectData"]["useOriginalRatio"], "cores you DON'T want this program to edit the aspect ratios of", "Please enter the core name as listed in the Cores/ directory, e.g. agg23.SNES")
                                elif action == "2":
                                    # This is pretty specific - we want to take a core name, load its video.json and take one of its entries as an input, then take as an input what its aspect ratio should be.
                                    # Also we should let you clear ones that are already there
                                    while True:
                                        system("cls")
                                        print("Here is the list of custom aspect ratios we've currently got:")
                                        for x in assistantData.dictionary["aspectData"]["useCustomRatio"].keys():
                                            print("\t" + x + ": " + str(assistantData.dictionary["aspectData"]["useCustomRatio"][x]))
                                        print("\nPlease give us a core name. If it's already in our database, we'll remove its custom ratios. If not, we'll add it. Or, just press Enter to go back!")
                                        action = input()
                                        if action == "":
                                            break
                                        elif action in assistantData.dictionary["aspectData"]["useCustomRatio"].keys():
                                            assistantData.dictionary["aspectData"]["useCustomRatio"].pop(action)
                                        elif action in listdir("../Cores"):
                                            videoJSON = OpenJSON("../Cores/" + action + "/video.json")
                                            print("\nOkay. Here are the available scaler modes for that core.")
                                            for x in range(len(videoJSON.dictionary["video"]["scaler_modes"])): #we take the index rather than the thing itself for easier readability on the user end
                                                print("\t" + str(x+1) + ". " + str(videoJSON.dictionary["video"]["scaler_modes"][x]))
                                            modeNum = input("Which number mode would you like to apply a custom aspect ratio to?")
                                            try:
                                                scalerMode = videoJSON.dictionary["video"]["scaler_modes"][int(modeNum) - 1]
                                                aspectHeight = input("What would you like the aspect ratio height to be?")
                                                aspectWidth = input("What would you like the aspect ratio width to be?")
                                                if not action in assistantData.dictionary["aspectData"]["useCustomRatio"].keys():
                                                    assistantData.dictionary["aspectData"]["useCustomRatio"][action] = []
                                                assistantData.dictionary["aspectData"]["useCustomRatio"][action].append({"aspect_h": int(aspectHeight), "aspect_w": int(aspectWidth), "height": scalerMode["height"], "width": scalerMode["width"]})
                                            except ValueError or KeyError:
                                                print("That's not one of the options... Please try again!")
                                                system("pause")
                                        else:
                                            print("That core doesn't seem to exist...")
                                            system("pause")
                                elif action == "3":
                                    assistantData.dictionary["aspectData"]["rotateBy90"] = edit_list(assistantData.dictionary["aspectData"]["rotateBy90"], "cores to rotate by 90 degrees", "Please enter the platform name that corresponds to the core, e.g. Contra.\nNote: if you have asset cleaning and core cloning turned on, this means you should enter the names of any games in particular you want rotated.")
                                elif action == "4":
                                    assistantData.dictionary["aspectData"]["rotateBy180"] = edit_list(assistantData.dictionary["aspectData"]["rotateBy180"], "cores to rotate by 180 degrees", "Please enter the platform name that corresponds to the core, e.g. Contra.\nNote: if you have asset cleaning and core cloning turned on, this means you should enter the names of any games in particular you want rotated.")
                                elif action == "5":
                                    assistantData.dictionary["aspectData"]["rotateBy270"] = edit_list(assistantData.dictionary["aspectData"]["rotateBy270"], "cores to rotate by 270 degrees", "Please enter the platform name that corresponds to the core, e.g. Contra.\nNote: if you have asset cleaning and core cloning turned on, this means you should enter the names of any games in particular you want rotated.")
                                elif action == "": #go back
                                    break
                        elif action == "":
                            assistantData.save()
                            break
                if action == "3": #Run make_image() with a custom image
                    replacePlatImage = input("What is the name of the platform whose image you want to replace?")
                    imageToReplace = input("What is the name of the image file you would like to replace it with, excluding extension?")
                    make_image(imageToReplace)
                    copy("../Updater/_assistantimages/" + imageToReplace + ".bin","../Platforms/_images/" + replacePlatImage + ".bin")
                if action == "4": #Reset settings
                    cleanBoolDict = {"clean":True,"autostart":True,"platforms":True,"integer":True,"rename":True,"favourites":True,"altcores":True,"image":True}
                    while True:
                        system("cls")
                        print("Would you like to keep any data already saved?\n")
                        print("\t1. Asset cleaning settings (which JSON files to keep for any cores with data saved).\n\tCurrently turned " + displayDictionary[cleanBoolDict["clean"]] + "\n")
                        print("\t2. Autostart settings (which cores to skip autostarting).\n\tCurrently turned " + displayDictionary[cleanBoolDict["autostart"]]+ "\n")
                        print("\t3. Platform cleaning settings (which platform categories are accepted and which are flagged up for user input).\n\tCurrently turned " + displayDictionary[cleanBoolDict["platforms"]]+ "\n")
                        print("\t4. Aspect ratio correction settings (which cores shouldn't be integer scaled, and which should be rotated).\n\tCurrently turned " + displayDictionary[cleanBoolDict["integer"]]+ "\n")
                        print("\t5. Core platform renaming settings (which cores' associated platform should be changed, and what to).\n\tCurrently turned " + displayDictionary[cleanBoolDict["rename"]]+ "\n")
                        print("\t6. Favourites (which games should have favourite cores generated for them).\n\tCurrently turned " + displayDictionary[cleanBoolDict["favourites"]]+ "\n")
                        print("\t7. Alt core settings (which cores should have copies made of them to allow for swapping between options on your device).\n\tCurrently turned " + displayDictionary[cleanBoolDict["altcores"]]+ "\n")
                        print("\t8. New image list (which cores should have a new platform image generated).\n\tCurrently turned " + displayDictionary[cleanBoolDict["image"]]+ "\n")
                        print("\t... Or just press Enter to continue to the reset!")
                        action = input()
                        if action == "1":
                            cleanBoolDict["clean"] = not cleanBoolDict["clean"]
                        if action == "3":
                            cleanBoolDict["platforms"] = not cleanBoolDict["platforms"]
                        if action == "4":
                            cleanBoolDict["integer"] = not cleanBoolDict["integer"]
                        if action == "2":
                            cleanBoolDict["autostart"] = not cleanBoolDict["autostart"]
                        if action == "5":
                            cleanBoolDict["rename"] = not cleanBoolDict["rename"]
                        if action == "6":
                            cleanBoolDict["favourites"] = not cleanBoolDict["favourites"]
                        if action == "7":
                            cleanBoolDict["altcores"] = not cleanBoolDict["altcores"]
                        if action == "8":
                            cleanBoolDict["image"] = not cleanBoolDict["image"]
                        if action == "":
                            break
                    system("cls")
                    print("Clearing data...\n\n")
                    
                    #Also have to delete assistant_data for this to work
                    nextAssistantData = baseAssistantData
                    
                    # You can keep everything except versionList data for cores without saved JSON files, and programSettings data (which you get asked for again anyway)
                    if cleanBoolDict["clean"]:
                        nextAssistantData["cleanData"] = assistantData.dictionary["cleanData"]
                        nextAssistantData["cleanData"]["nextVersionList"] = {}
                        for x in assistantData.dictionary["cleanData"]["cores"]:
                            nextAssistantData["cleanData"]["nextVersionList"][x] = "0"
                    if cleanBoolDict["platforms"]:
                        nextAssistantData["platformFixData"] = assistantData.dictionary["platformFixData"]
                    if cleanBoolDict["integer"]:
                        nextAssistantData["aspectData"] = assistantData.dictionary["aspectData"]
                    if cleanBoolDict["autostart"]:
                        nextAssistantData["autostartData"] = assistantData.dictionary["autostartData"]
                    if cleanBoolDict["rename"]:
                        nextAssistantData["platformRenameData"] = assistantData.dictionary["platformRenameData"]
                    if cleanBoolDict["favourites"]:
                        nextAssistantData["favouriteData"] = assistantData.dictionary["favouriteData"]
                    if cleanBoolDict["altcores"]:
                        nextAssistantData["altCoreData"] = assistantData.dictionary["altCoreData"]
                    remove("assistant_data.json")
                    setup_data(nextAssistantData)
                    break
                elif action == "5": #Exit program
                    break
        assistantData.save()
    else:
        input("For this program to run, it requires: \n\tThe pocker_updater.exe utility from https://github.com/mattpannella/pocket-updater-utility/releases, to be placed in the same folder as this program\n\tThe image processor, downloaded from https://github.com/agg23/Analogue-Pocket-Image-Process/tree/master, to be placed in Updater/_assistantimages/Analogue-Pocket-Image-Process-master - note: this requires a node.js installation from https://nodejs.org/en/download\n\nYou're missing at least one of these, so please check which and rerun the program when you're ready!")

main()