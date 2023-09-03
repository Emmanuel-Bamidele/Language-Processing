"""
Text Editor Application
Author: Emmanuel Bamidele
License: MIT
Instructions:
1. Install required modules using: pip install nltk spellchecker
2. Run the script to launch the Text Editor application.
3. Enter or paste text in the 'Original Text' box.
4. Click the 'Correct Text' button to correct spelling errors in the 'Corrected Text' box.
5. Select text in the 'Corrected Text' box and right-click to see synonyms and alternative spellings.
6. Double-click on a synonym or alternative spelling to replace the selected text.
7. Click the 'Paraphrase' button to paraphrase the selected text from the 'Corrected Text' box in the 'Paraphrased Text' box.
8. The 'Synonyms' box displays synonyms of the selected word, and the 'Alternative Spellings' box shows alternative spellings.
9. To clear text boxes, click the 'Clear' button on the top-right corner of each text box.
10. The 'Step-by-Step Guide' box provides a quick overview of the process.
11. To clear all text boxes, click the 'Clear All' button at the bottom-right.
"""

import re
import tkinter as tk
from tkinter import ttk
from spellchecker import SpellChecker
import random
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, WordPunctTokenizer
from nltk import pos_tag

# Initialize spell checker
spell = SpellChecker()


# Paraphrase adjectives by replacing them with their synonyms
def paraphrase_sentence(sentence):
    # Tokenize and tag parts of speech
    words = word_tokenize(sentence)
    pos_tags = pos_tag(words)

    paraphrased_words = []

    for word, pos in pos_tags:
        if pos == 'JJ':  # 'JJ' tag represents an adjective
            synonyms = set()
            for syn in wordnet.synsets(word, pos='a'):  # 'a' specifies to only find adjectives
                for lemma in syn.lemmas():
                    synonyms.add(lemma.name())

            if len(synonyms) > 1:
                paraphrased_words.append(random.choice(list(synonyms - {word})))
            else:
                paraphrased_words.append(word)
        else:
            paraphrased_words.append(word)

    paraphrased_sentence = ' '.join(paraphrased_words)

    # Remove space before each punctuation mark
    paraphrased_sentence = re.sub(r'\s([?.!,:;"](?:\s|$))', r'\1', paraphrased_sentence)

    return paraphrased_sentence


# Correct spelling errors in the text
def correct_spelling(text):
    corrected_text = []
    # Split by whitespace to preserve the original formatting and spacing
    for segment in text.split():
        # Find all words and their preceding punctuation
        words_with_punct = re.findall(r'([!.,;?]*)(\w+)([!.,;?]*)', segment)
        for pre_punct, word, post_punct in words_with_punct:
            corrected_word = spell.correction(word)
            # Preserve capitalization of the first letter
            if word[0].isupper():
                corrected_word = corrected_word.capitalize()
            corrected_text.append(f'{pre_punct}{corrected_word}{post_punct}')

    return ' '.join(corrected_text)


# Update the corrected Text widget
def update_output():
    original_text = original_text_widget.get("1.0", "end-1c")
    corrected_text = correct_spelling(original_text)
    corrected_text_widget.delete("1.0", tk.END)
    corrected_text_widget.insert(tk.END, corrected_text)


# Update the paraphrase Text widget
def update_paraphrase():
    original_text = corrected_text_widget.get("1.0", tk.END).strip()  # Get the full text
    try:
        selected_text = corrected_text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)  # Get the selected text
    except tk.TclError:  # No text is selected
        return

    # Get the start and end indices of the selected text
    start_idx = corrected_text_widget.index(tk.SEL_FIRST)
    end_idx = corrected_text_widget.index(tk.SEL_LAST)

    # Break the original text into three parts
    before_selected = corrected_text_widget.get("1.0", start_idx)
    after_selected = corrected_text_widget.get(end_idx, tk.END)

    # Paraphrase the selected text
    paraphrased = paraphrase_sentence(selected_text)

    # Reconstruct the text with the paraphrased portion
    reconstructed_text = before_selected + after_selected  # Remove selected_text from the middle

    paraphrase_text_widget.delete("1.0", tk.END)
    paraphrase_text_widget.insert(tk.END, before_selected)

    # Insert each word from the paraphrased text, and tag it if it changed
    words_original = selected_text.split()
    words_paraphrased = paraphrased.split()
    words_corrected = correct_spelling(selected_text).split()  # Corrected version of selected_text

    for orig, para, corr in zip(words_original, words_paraphrased, words_corrected):
        if para != corr:
            # If the paraphrased word is different from the corrected word
            paraphrase_text_widget.insert(tk.END, para + " ", "changed")
        else:
            # If the paraphrased word is the same as the corrected word
            paraphrase_text_widget.insert(tk.END, para + " ")

    # Insert the rest of the text
    paraphrase_text_widget.insert(tk.END, after_selected)

    # Configure the 'changed' tag with italics and bold
    paraphrase_text_widget.tag_configure("changed", font=("TkDefaultFont", 10, "italic"), background="yellow")

    # Apply the 'selectable' tag to all text
    paraphrase_text_widget.tag_add("selectable", "1.0", tk.END)


# Get synonyms and alternative spellings of the selected word
def get_synonyms_and_spellings(event, text_widget):
    cursor_position = text_widget.index(tk.INSERT)
    line, col = map(int, cursor_position.split('.'))
    word_start = text_widget.index(f"{line}.{col} wordstart")
    word_end = text_widget.index(f"{line}.{col} wordend")
    word = text_widget.get(word_start, word_end)

    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())

    alternative_spellings = spell.candidates(word)

    synonym_listbox.delete(0, tk.END)
    spelling_listbox.delete(0, tk.END)
    for synonym in synonyms:
        synonym_listbox.insert(tk.END, synonym)
    for spelling in alternative_spellings:
        spelling_listbox.insert(tk.END, spelling)


# Replace the selected word with the chosen synonym or spelling
def replace_with_choice(event, text_widget, listbox):
    if not listbox.curselection():
        return

    selected_choice = listbox.get(listbox.curselection())
    cursor_position = text_widget.index(tk.INSERT)
    line, col = map(int, cursor_position.split('.'))
    word_start = text_widget.index(f"{line}.{col} wordstart")
    word_end = text_widget.index(f"{line}.{col} wordend")

    text_widget.delete(word_start, word_end)
    text_widget.insert(word_start, selected_choice)


# Function to apply blue highlight to selected text
def apply_blue_highlight(text_widget):
    text_widget.tag_add(tk.SEL, '1.0', tk.END)
    text_widget.tag_configure("blue_highlight", background="blue", foreground="white")
    text_widget.tag_add("blue_highlight", tk.SEL_FIRST, tk.SEL_LAST)


# Function to clear all text boxes
def clear_all():
    original_text_widget.delete('1.0', tk.END)
    corrected_text_widget.delete('1.0', tk.END)
    paraphrase_text_widget.delete('1.0', tk.END)
    synonym_listbox.delete(0, tk.END)
    spelling_listbox.delete(0, tk.END)


# GUI setup
root = tk.Tk()
root.title("Text Editor | ©Emmanuel Bamidele | version 1")

# Labels
tk.Label(root, text="Original Text:").grid(row=0, column=0, columnspan=1)
tk.Label(root, text="Corrected Text:").grid(row=0, column=1, columnspan=2)
tk.Label(root, text="Paraphrased Text:").grid(row=2, column=0, columnspan=1)

# Span the Synonyms and Alternative Spellings labels across 2 columns
tk.Label(root, text="Synonyms:").grid(row=2, column=1, columnspan=1)
tk.Label(root, text="Alternative Spellings:").grid(row=2, column=2, columnspan=1)

# Text widgets with larger height and width
original_text_widget = tk.Text(root, wrap=tk.WORD, height=20, width=60)
corrected_text_widget = tk.Text(root, wrap=tk.WORD, height=20, width=60)
paraphrase_text_widget = tk.Text(root, wrap=tk.WORD, height=20, width=60)
synonym_listbox = tk.Listbox(root, height=20, width=30)
spelling_listbox = tk.Listbox(root, height=20, width=30)

# Set up row and column weights for resizing
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Buttons
update_button = ttk.Button(root, text="Correct Text", command=update_output)
paraphrase_button = ttk.Button(root, text="Paraphrase", command=update_paraphrase)

# Place "Clear" buttons on the top-right corner of each text box
clear_original_button = ttk.Button(root, text="Clear", command=lambda: original_text_widget.delete('1.0', tk.END))
clear_original_button.place(x=410, y=15)

# Place "Paste" button on the top-right corner of the original text box
paste_original_button = ttk.Button(root, text="Paste", command=lambda: original_text_widget.insert('1.0', root.clipboard_get()))
paste_original_button.place(x=320, y=15)

# Place "Select All" button on top-right corner of corrected text box
select_all_corrected_button = ttk.Button(root, text="Select All", command=lambda: apply_blue_highlight(corrected_text_widget))
select_all_corrected_button.place(x=920, y=15)

# Place "Copy All" button on top-right corner of paraphrased text box
copy_all_paraphrase_button = ttk.Button(root, text="Copy All", command=lambda: [root.clipboard_clear(), root.clipboard_append(paraphrase_text_widget.get('1.0', tk.END))])
copy_all_paraphrase_button.place(x=410, y=385)

# Create a button to clear all text boxes
clear_all_button = ttk.Button(root, text="Reset", command=clear_all)
clear_all_button.place(x=920, y=735)  # Placed at bottom-right

# Grid layout
original_text_widget.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
corrected_text_widget.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
paraphrase_text_widget.grid(row=3, column=0, columnspan=1, padx=10, pady=10)
synonym_listbox.grid(row=3, column=1, columnspan=1, padx=10, pady=10)
spelling_listbox.grid(row=3, column=2, columnspan=1, padx=10, pady=10)
update_button.grid(row=4, column=0, columnspan=1, padx=10, pady=10)
paraphrase_button.grid(row=4, column=1, columnspan=1, padx=10, pady=10)

# Event bindings
corrected_text_widget.bind("<Button-3>", lambda event: get_synonyms_and_spellings(event, corrected_text_widget))
paraphrase_text_widget.bind("<Button-3>", lambda event: get_synonyms_and_spellings(event, paraphrase_text_widget))
synonym_listbox.bind("<Double-Button-1>",
                     lambda event: replace_with_choice(event, corrected_text_widget, synonym_listbox))
spelling_listbox.bind("<Double-Button-1>",
                      lambda event: replace_with_choice(event, corrected_text_widget, spelling_listbox))
synonym_listbox.bind("<Double-Button-3>",
                     lambda event: replace_with_choice(event, paraphrase_text_widget, synonym_listbox))
spelling_listbox.bind("<Double-Button-3>",
                      lambda event: replace_with_choice(event, paraphrase_text_widget, spelling_listbox))

root.mainloop()