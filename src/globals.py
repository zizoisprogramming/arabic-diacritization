import re
import pickle

DIACRITICS_PATTERN = re.compile(r'[\u064B-\u0652]')


def split_text_and_diacritics(text):

    letters = []
    labels = []
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if DIACRITICS_PATTERN.match(char):
            if labels:
                labels[-1] += char
        else:
            letters.append(char)
            labels.append("") 
            
        i += 1
        
    return "".join(letters), labels


def post_process(test_results):
    with open('/home/zizo/Documents/NLP/Project/utils/arabic_letters.pickle' , 'rb') as f:
        arabic_letters = pickle.load(f)

    cleaned_test_results = []
    for line in test_results:
        cleaned_text, labels = split_text_and_diacritics(line)
        new_text = ''
        for i in range(len(cleaned_text)):
            if cleaned_text[i] in arabic_letters or cleaned_text[i] == ' ':
                new_text += cleaned_text[i] + labels[i]
            

        cleaned_test_results.append(new_text)
        print(new_text)

    return cleaned_test_results

post_process(["وَلَا عِدَّةَ عَلَى أَمَةٍ وَمُدَبَّرَةٍ كَانَ يَطَؤُهَا لِعَدَمِ الْفِرَاشِ جَوْهَرَةٌ ( وَ ) كَذَا ( مَوْطُوءَةٌ بِشُبْهَةٍ ) كَمَزْفُوفَةٍ لِغَيْرِ بَعْلِهَا ( أَوْ نِكَاحٍ فَاسِدٍ ) ."])