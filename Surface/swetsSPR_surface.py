import serial, os, time, signal, random, string, numpy, csv, codecs
from psychopy import visual, event, core, logging, gui, sound, data
from CSL import latinSquare as latin_square

##### SETTINGS ################################################################

# Where do I find the items?
item_file = 'swets_surface_items.txt'

# Where do I find the practice items?
practice_file = 'swets_practice.txt'

# Duration of fixation cross.
fix_time = 1.5

# Time between words.
between_words_time = .100

# Response deadline.
deadline = 10.000

# Questioni response deadline.
qDeadline = 60.000

# Time error message is on.
error_time = 5.000

# Overlong error message.
timeout_text = 'Too slow!'

# Number of lists.
number_lists = 3

# Boolean; do stimuli require use of Unicode (must be 'UTF-8')?
using_unicode = True

def format(text):
    """
    Formats text from items file.
    """
    return text.replace('_', ' ')

def decode_unicode(text):
    """
    Return decoded Unicode text if needed.
    """
    return text.decode('utf-8') if using_unicode else text

##### COLLECT USER DETAILS ####################################################

# Look in results folder to determine the appropriate subject number.
if not os.path.exists(os.getcwd() + '/swets_surface_results/'): os.makedirs(os.getcwd() + '/swets_surface_results/')
results_files = os.listdir(os.getcwd() + '/swets_surface_results/')
if len(results_files) != 0: subjects_run = [int(s.split('.')[0]) for s in results_files if s not in ['.DS_Store', 'Icon\r']]
else: subjects_run = [0]
current_subject_number = max(subjects_run) + 1

# Show dialog and wait for OK or Cancel.
subject_info = gui.Dlg(title = 'Swets Replication: SPR Surface Condition')
subject_info.addField('Subject Number:', current_subject_number)
subject_info.addField('Age:', 21)
subject_info.addField('Gender:', 'M')
subject_info.show()

# The user pressed OK.
if gui.OK:
    current_subject_number = int(subject_info.data[0])
# The user pressed Cancel.
else:
    print('User cancelled')

#### Create output
data = open(os.getcwd() + "/swets_surface_results/" + str("%03d" % (current_subject_number,)) + ".txt", "w")      ## Open output file channel for editing
data.write('trial\tsubj\tage\tgender\tstimulustype\titem\tcondition\tword\tposition\trt\tcorrect\n')     ## add header
data.close()

##### INITIALIZE THE EXPERIMENT ###############################################

# Calculate current list based on subject number.
current_list = current_subject_number % number_lists + \
               ((not current_subject_number % number_lists) * number_lists)

# Get experimental items and randomize.
experimental_items = latin_square(current_list, item_file)


with open(practice_file) as csvFile:
        practiceFile = csv.reader(csvFile)
        practiceList = [item for item in practiceFile]


# Set up stimulus window.
stim_window = visual.Window(fullscr = True)


# Feedback screen.
timeout_feedback = visual.TextStim(stim_window,
                                   text=timeout_text,
                                   pos=(0.0, 0.0),
                                   bold=True,
                                   height=.15,
                                   color=[1, -1, -1])

# Break screen.
breakText = visual.TextStim(
    stim_window,
    text="Please take a short break. Press any key to continue",
    pos=(0.0, 0.0),
    height=.075)

##### PRACTICE SCREEN #########################################################

def practice():
    """
    Practice screen.
    """
    # This is the introduction screen
    sprInstructions = visual.TextStim(
        stim_window,
        text='Welcome! In this experiment, you will be reading each sentence one word at a time, and then answering a comprehension question about it. Before each trial, you will see a cross in the center of the screen. When the cross disappears, you will see the first word of the sentence. To see the next word, press the space bar. Continue pressing the spar to reveal each subsequent word until the sentence is finished. Please try to press the spacebar so that you can read the sentence at a natural pace. As much as possible, you should be pressing the spacebar so that you are reading the sentence as though you were seeing it all at once. Press any key to see more instructions.',
        pos=(0.0, 0.0),
        height=.075)

    sprInstructions.draw()
    stim_window.flip()
    event.waitKeys()
    stim_window.flip()

    event.clearEvents()
    questionInstructions = visual.TextStim(
        stim_window,
        text = "After each sentence, you will see a comprehension question which tests your understanding of what the sentence meant. For each comprehension question, there will be two possible answers: one on the left, and one on the right. Based on your understanding of the sentence, press the 'f' key if you think the answer on the left is correct, and the 'j' key if you think the answer on the right is correct. Please do your best to understand each sentence as you read it so that you can answer the comprehension question accurately! Press any key to start the practice session. ",
        pos=(0.0, 0.0),
        height = 0.075)

    questionInstructions.draw()
    stim_window.flip()

    event.waitKeys()
    stim_window.flip()
    
    # This is for displaying the practice items. Responses are not recorded.
    for item in practiceList:
        # Parse sentence from item: Split on white space, underscores replaced
        # with spaces.
        sentence = [format(word) for word in item[3].split()]

        # Run item.
        response = sprTrial(sentence)

        # Run question
        if(len(item)>4) and response[-1][2]!='NA': questionTrial(item[4:])

    # A buffer screen between the practice items and the experiment.
    buffer = visual.TextStim(
        stim_window,
        text="REMINDER: Your hands should be positioned so that your thumbs are on the spacebar and your index fingers are on the 'f' and 'j' keys. After the fixation cross, press the spacebar to progress through the sentence. To answer the questions, press the 'f' key to choose the answer on the left, and the 'j' key to choose the answer on the right. Every 20 trials you will have the opportunity to take a break. We recommend that you take this time to stand up, stretch, and prepare yourself for the remainder of the experiment. If you have any further questions, or wish to quit the experiment, please speak with the researcher now. Press any key to continue the experiment.",
        pos=(0.0, 0.0),
        height=.075)

    buffer.draw()
    stim_window.flip()

    event.waitKeys()
    stim_window.flip()

##### MAIN EXPERIMENT LOOP ####################################################

def main():
    """
    Main experiment loop.
    """
    for trialNum, item in enumerate(experimental_items):
        # Parse sentence from item: Split on white space, underscores replaced
        # with spaces.
        sentence = [format(word) for word in item[3].split()]

        # Run item.
        response = sprTrial(sentence)

        # Print out the results.
        #print (subject_info.data,item,response)
        for word in response:
            data = open(os.getcwd() + "/swets_surface_results/" + str("%03d" % (current_subject_number,)) + ".txt", "a")
            data.write("\t".join([str(trialNum)]+map(str, subject_info.data)+map(str, item[0:3])+map(str,word))+"\n")
            data.close()
        
        # Run question
        if(len(item)>4) and response[-1][2]!='NA': 
            qresponse = questionTrial(item[4:])
            data = open(os.getcwd() + "/swets_surface_results/" + str("%03d" % (current_subject_number,)) + ".txt", "a")
            data.write("\t".join([str(trialNum)]+map(str, subject_info.data)+['Question']+map(str, item[1:3])+map(str,qresponse))+"\n")
            data.close()


        # Include break after a certain number of trials
        if trialNum > 0 and trialNum % 20 == 0 :
            breakText.draw()
            stim_window.flip()
            event.waitKeys()

    data.close()
    event.clearEvents()
    endExperiment = visual.TextStim(
        stim_window,
        text = "That's all for the experiment! Please see the researcher for debriefing.",
        pos=(0.0, 0.0),
        height = 0.075)

    endExperiment.draw()
    stim_window.flip()

    event.waitKeys()


def sprTrial(sentence):
    """
    Experiment trial.
    """

    # Clear any key log.
    deadlineClock = core.Clock()

    # Decode sentence before presentation if using Unicode.
    #sentence = map(decode_unicode, sentence)

    # Display fixation point.
    fixation = visual.TextStim(
        stim_window,
        text='+',
        pos=(0.0, 0.0),
        bold=True,
        height=0.15)
    fixation.draw()
    stim_window.flip()

    core.wait(fix_time)
    stim_window.flip()

    # Display sentence word-by-word, but allow the final word to be distinct font or color.
    event.clearEvents()
    deadlineClock.reset()
    response = []
    current_word_position = 1

    for word in sentence:
        current_word_response = []

        while len(current_word_response) == 0 and deadlineClock.getTime() < deadline:
            stim = visual.TextStim(
                stim_window,
                text=word,
                pos=(0.0, 0.0),
                bold=True,
                height=0.15)
            stim.draw()
            stim_window.flip()
            current_word_response = event.getKeys(keyList = ["space", "escape"])
            current_rt = deadlineClock.getTime()

        if deadlineClock.getTime() > deadline:
            timeout_feedback.draw()
            stim_window.flip()
            core.wait(1)
            stim_window.flip()
            response.append([word, current_word_position, 'NA', 'NA'])
            break
        elif "escape" in current_word_response: 
            core.quit()
        else: 
            response.append([word, current_word_position, round(1000*current_rt), 'NA'])
            current_word_position += 1

        core.wait(between_words_time)
        deadlineClock.reset()
        event.clearEvents()

    return response

def questionTrial(question):
    deadlineClock = core.Clock()
    event.clearEvents()
    deadlineClock.reset()

    if question[1]=="Yes":
        answer1_position = -0.25
        correct_response = "f"
    elif question[1]=="No":
        answer1_position = 0.25
        correct_response = "j"
    elif random.randint(1,11)%2 == 0: 
        answer1_position = -0.25
        correct_response = "f"
    else:
        answer1_position = 0.25
        correct_response = "j"
    answer = []

    while len(answer) == 0 and deadlineClock.getTime() < qDeadline:
        stim = visual.TextStim(
            stim_window,
            text=format(question[0]),
            pos=(0.0, 0.0),
            bold=True,
            height=0.075)
        answer1 = visual.TextStim(
            stim_window,
            text=format(question[1]),
            pos=(answer1_position, -.25),
            bold=True,
            height=0.075)
        answer2 = visual.TextStim(
            stim_window,
            text=format(question[2]),
            pos=(-answer1_position, -0.25),
            bold=True,
            height=0.075)
        stim.draw()
        answer1.draw()
        answer2.draw()
        stim_window.flip()
        answer = event.getKeys(keyList = ["f", "j", "escape"])
        answer_rt = deadlineClock.getTime()

    if deadlineClock.getTime() > qDeadline:
        timeout_feedback.draw()
        stim_window.flip()
        core.wait(1)
        stim_window.flip()
        response = ['QUESTION', 'NA', 'NA', 'NA']
    if "escape" in answer: 
        core.quit()
    else:
        response = ['NA', 'NA', round(1000*answer_rt), int(correct_response in answer)]

    return response


##### RUNTIME #################################################################

practice()
main()
stim_window.close()
core.quit()